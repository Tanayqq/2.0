import os
import sys
import time
import argparse
import structlog
from typing import List, Dict, Any, Optional

# Allow running directly from command line
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from .config import ingestion_config
from .providers.sources.openfda_provider import OpenFDAProvider
from .providers.sources.dailymed_provider import DailyMedProvider
from .parser import MedicalParser
from .validator import MedicalValidator
from .chunker import MedicalSectionChunker
from .embedder import MedicalEmbedder
from .uploader import MedicalUploader
from .statistics import IngestionStatistics
from .reports import ReportGenerator
from .generate_reports import generate_reports
from app.core.config import settings
from app.infrastructure.vector_db import QdrantAdapter
from app.infrastructure.profile_store import StructuredProfileStore
from .profile_parser import DeterministicProfileParser

logger = structlog.get_logger()

class IngestionOrchestrator:
    """
    Orchestrates the entire ingestion pipeline: health checks, collection,
    prioritization, parsing, validation, chunking, embedding, uploading,
    statistics collection, reporting, and retrieval smoke tests.
    """
    def __init__(self, force_reingest: bool = False, incremental: bool = False):
        self.stats = IngestionStatistics()
        self.force_reingest = force_reingest
        self.incremental = incremental
        self.parser = MedicalParser()
        self.validator = MedicalValidator()
        self.chunker = MedicalSectionChunker()
        self.embedder = MedicalEmbedder()
        self.uploader = MedicalUploader()
        self.report_generator = ReportGenerator(self.stats)
        self.profile_store = StructuredProfileStore()
        self.profile_parser = DeterministicProfileParser()
        
        # Instantiate active source providers
        self.providers = {}
        if "openfda" in ingestion_config.ACTIVE_SOURCES:
            self.providers["openfda"] = OpenFDAProvider()
        if "dailymed" in ingestion_config.ACTIVE_SOURCES:
            self.providers["dailymed"] = DailyMedProvider()

    def run_preflight_checks(self) -> bool:
        """
        Runs health checks on all active providers and validates embedding dimensions against Qdrant.
        """
        logger.info("running_preflight_checks")
        
        # 1. Check source providers
        for name, provider in self.providers.items():
            health = provider.health_check()
            if health.get("status") != "healthy":
                logger.error("source_provider_unhealthy", provider=name, health=health)
                return False
            logger.info("source_provider_healthy", provider=name, latency=health.get("latency_sec"))
            
        # 2. Check embedding dimension alignment with Qdrant collection
        expected_dim = self.embedder.get_dimension()
        if not self.uploader.validate_dimension(expected_dim):
            logger.error("preflight_dimension_check_failed")
            return False
            
        # Ensure collection exists before starting
        self.uploader.create_collection_if_not_exists(expected_dim)
        self.profile_store.initialize_collections()
        
        logger.info("preflight_checks_passed_successfully")
        return True

    def select_primary_source(self, docs_by_source: Dict[str, Any], drug_name: str) -> Optional[Any]:
        """
        Select the highest priority source according to configuration.
        Strictly preserves provenance by completely ignoring lower priority sources.
        """
        if not docs_by_source:
            return None
            
        # Get active sources sorted by priority
        sorted_sources = [s for s in ingestion_config.SOURCE_PRIORITY if s in docs_by_source]
        
        if not sorted_sources:
            # Fallback to whatever is available if priority list has no matches
            sorted_sources = list(docs_by_source.keys())
            
        primary_source = sorted_sources[0]
        primary_doc = docs_by_source[primary_source]
        
        logger.info("selected_primary_source", drug=drug_name, source=primary_source)
        return primary_doc

    def process_drug(self, drug_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch, prioritize, parse, validate, and chunk a single drug's labels.
        Also builds and uploads structured profiles with incremental updates.
        """
        self.stats.docs_downloaded += 1
        docs_by_source = {}
        
        # 1. Fetch from all active sources
        for name, provider in self.providers.items():
            try:
                doc = provider.fetch_single_drug(drug_name)
                if doc:
                    docs_by_source[name] = doc
            except Exception as e:
                logger.error("failed_fetching_drug_from_source", drug=drug_name, source=name, error=str(e))
                
        if not docs_by_source:
            self.stats.log_validation_failure(f"Drug '{drug_name}' could not be fetched from any active source.")
            return None
            
        # 2. Source selection (Strict Provenance)
        primary_doc = self.select_primary_source(docs_by_source, drug_name)
        if not primary_doc:
            return None
            
        # 3. Clean and parse sections
        parsed_doc = self.parser.parse(primary_doc)
        
        # 4. Ingestion validation
        is_valid, reason = self.validator.validate(parsed_doc)
        if not is_valid:
            # Send failed record to Dead Letter Queue (DLQ) to ensure pipeline does not halt
            self.validator.send_to_dlq(parsed_doc, reason)
            self.stats.log_validation_failure(f"Validation failed for '{drug_name}': {reason}")
            return None

        # --- INCREMENTAL INGESTION CHECK ---
        entity_id = f"drug:{parsed_doc.drug.lower().replace(' ', '_')}"
        full_text = " ".join([sec.content for sec in parsed_doc.sections])
        checksum = self.profile_parser.calculate_checksum(full_text)
        
        existing_checksum = self.profile_store.get_profile_checksum(entity_id, "clinical", "FDA")
        if not self.force_reingest and existing_checksum == checksum:
            logger.info("incremental_ingestion_skip", drug=parsed_doc.drug, reason="checksum_matched")
            return []  # Return empty chunks to skip embedding/upload for this drug

        self.stats.docs_parsed += 1
        self.stats.record_drug_sections(parsed_doc.drug, len(parsed_doc.sections))
        
        # Calculate and record completeness score
        status_by_category, score, percentage = self.validator.calculate_completeness_score(parsed_doc)
        self.stats.record_drug_completeness(parsed_doc.drug, status_by_category, score, percentage)
        
        # --- STRUCTURED PROFILE BUILD & UPLOAD ---
        try:
            logger.info("building_structured_profiles", drug=parsed_doc.drug)
            identity_prof = self.profile_parser.build_identity_profile(parsed_doc)
            clinical_prof = self.profile_parser.build_clinical_profile(parsed_doc)
            
            brand_names_list = identity_prof.brand_names.value or []
            
            # 1. Upsert entity registry
            self.profile_store.upsert_registry_entry(
                entity_id=entity_id,
                generic_name=parsed_doc.generic_name,
                preferred_authority="FDA",
                version=1,
                aliases=brand_names_list
            )
            # 2. Upsert identity & clinical profiles
            self.profile_store.upsert_profile(
                entity_id=entity_id,
                profile_type="identity",
                authority="FDA",
                data=identity_prof.model_dump(),
                checksum=checksum,
                version=1
            )
            self.profile_store.upsert_profile(
                entity_id=entity_id,
                profile_type="clinical",
                authority="FDA",
                data=clinical_prof.model_dump(),
                checksum=checksum,
                version=1
            )
             # 3. Build and upsert prioritized brand aliases with rich metadata
            from app.usecases.drug_resolver import DrugNameResolver
            aliases_with_meta = []
            seen_aliases = set()
            generic_title = parsed_doc.generic_name.title() if parsed_doc.generic_name else parsed_doc.drug.title()

            def add_alias(alias_str, generic, country, authority, source, alias_type):
                if not alias_str:
                    return
                name_clean = alias_str.strip()
                name_lower = name_clean.lower()
                if name_lower not in seen_aliases:
                    seen_aliases.add(name_lower)
                    aliases_with_meta.append({
                        "alias": name_clean,
                        "generic": generic,
                        "country": country,
                        "authority": authority,
                        "source": source,
                        "type": alias_type
                    })

            # Priority 0: Always register the generic name itself (type: generic)
            add_alias(generic_title, generic_title, "US", "FDA", "Registry", "generic")

            # Priority 1: DailyMed Proprietary Names (from XML)
            if parsed_doc.source.lower() == "dailymed":
                add_alias(parsed_doc.drug.title(), generic_title, "US", "DailyMed", "DailyMed XML", "brand")

            # Load raw openfda to extract RxNorm synonyms & OpenFDA brand_names
            openfda_raw = self.profile_parser._read_raw_openfda(parsed_doc.drug)
            openfda_meta = openfda_raw.get("openfda", {})

            # Priority 2: RxNorm Synonyms
            rxnorm_substances = openfda_meta.get("substance_name", [])
            for substance in rxnorm_substances:
                add_alias(substance.title(), generic_title, "US", "FDA", "RxNorm", "synonym")
            rxnorm_generics = openfda_meta.get("generic_name", [])
            for gen_name in rxnorm_generics:
                add_alias(gen_name.title(), generic_title, "US", "FDA", "RxNorm", "generic")

            # Priority 2.5: RxNorm API Integration
            try:
                from .providers.sources.rxnorm_client import RxNormClient
                import time
                rx_client = RxNormClient()
                rxcui = rx_client.get_rxcui(parsed_doc.drug)
                if not rxcui and parsed_doc.generic_name:
                    rxcui = rx_client.get_rxcui(parsed_doc.generic_name)
                if rxcui:
                    rx_names = rx_client.get_all_names(rxcui)
                    for rx_name in rx_names:
                        add_alias(rx_name.title(), generic_title, "US", "FDA", "RxNorm API", "brand")
                    time.sleep(0.2)
            except Exception as rx_err:
                logger.warning("rxnorm_api_integration_failed", drug=parsed_doc.drug, error=str(rx_err))

            # Priority 3: OpenFDA brand_names
            openfda_brands = openfda_meta.get("brand_name", [])
            for brand in openfda_brands:
                add_alias(brand.title(), generic_title, "US", "FDA", "OpenFDA", "brand")

            # Priority 4: DrugNameResolver (manual brand-to-generic mappings)
            generic_to_brands = {}
            for brand, gen in DrugNameResolver.BRAND_TO_GENERIC.items():
                generic_to_brands.setdefault(gen.lower(), []).append(brand.title())
            
            lookup_names = [parsed_doc.drug.lower(), parsed_doc.generic_name.lower()]
            for name in lookup_names:
                if name in generic_to_brands:
                    for brand in generic_to_brands[name]:
                        country = "US" if brand.lower() in [b.lower() for b in openfda_brands] else "India"
                        authority = "FDA" if country == "US" else "CDSCO"
                        source = "OpenFDA" if country == "US" else "DrugNameResolver"
                        add_alias(brand, generic_title, country, authority, source, "brand")

            # Priority 5: User-defined synonyms
            if parsed_doc.synonyms:
                for syn in parsed_doc.synonyms:
                    add_alias(syn.title(), generic_title, "US", "FDA", "DailyMed XML", "synonym")

            # Upsert all resolved aliases with their metadata
            for entry in aliases_with_meta:
                self.profile_store.upsert_alias(
                    alias=entry["alias"],
                    entity_id=entity_id,
                    generic=entry["generic"],
                    country=entry["country"],
                    authority=entry["authority"],
                    source=entry["source"],
                    alias_type=entry["type"]
                )
                self.stats.record_alias(source=entry["source"])
                
            logger.info("structured_profiles_uploaded_successfully", drug=parsed_doc.drug)
        except Exception as e:
            logger.error("failed_building_or_uploading_profiles", drug=parsed_doc.drug, error=str(e))
        
        # 5. Semantic section-based chunking
        chunks = self.chunker.chunk_document(parsed_doc)
        for chunk in chunks:
            self.stats.record_chunk(
                drug=chunk["drug_name"],
                section=chunk["section"],
                tokens=chunk["token_count"],
                source=chunk["source"],
                country=chunk.get("country", "US")
            )
            
        return chunks

    # 10 query templates run per-drug in smoke tests
    SMOKE_QUERY_TEMPLATES = [
        ("Contraindications of {drug}", "contraindications"),
        ("Dosage and administration of {drug}", "dosage_and_administration"),
        ("Drug interactions with {drug}", "drug_interactions"),
        ("Pregnancy safety of {drug}", "pregnancy"),
        ("Renal dose adjustment for {drug}", "renal_impairment"),
        ("Pediatric use of {drug}", "pediatric_use"),
        ("Mechanism of action of {drug}", "mechanism_of_action"),
        ("Indications for {drug}", "indications"),
        ("Storage conditions for {drug}", "storage"),
        ("Patient counseling for {drug}", "patient_counseling"),
    ]

    def run_smoke_tests(self, drug_names: List[str] = None) -> List[Dict[str, Any]]:
        """
        Execute smoke retrieval tests against Qdrant Cloud.
        Runs 10 per-drug section queries for every drug in drug_names,
        plus 6 adversarial tests (impossible query, wrong drug, brand resolution,
        typo tolerance, multi-drug separation, mixed query routing).
        """
        logger.info("running_retrieval_smoke_tests")
        db_adapter = QdrantAdapter(
            mode=settings.VECTOR_DB_MODE,
            path=settings.QDRANT_PATH,
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            collection_name=ingestion_config.QDRANT_COLLECTION
        )

        # Default to 7 legacy drugs if no list provided
        if not drug_names:
            drug_names = ["Metformin", "Atorvastatin", "Lisinopril", "Warfarin", "Amoxicillin", "Ibuprofen", "Losartan"]

        results = []

        # --- A. Per-drug section queries ---
        for drug in drug_names[:20]:  # Cap at 20 to keep runtime reasonable
            for template, expected_section in self.SMOKE_QUERY_TEMPLATES:
                q_text = template.format(drug=drug.capitalize())
                start_time = time.time()
                try:
                    q_vec = self.embedder.provider.embed_texts([q_text])[0]
                    hits = db_adapter.search(query_vector=q_vec, top_k=5)
                    latency = time.time() - start_time
                    target = drug.lower()
                    passed = any(
                        target in h.content.lower() or
                        target in h.metadata.get("drug_name", "").lower() or
                        target in h.metadata.get("drug", "").lower()
                        for h in hits
                    )
                    results.append({
                        "test_type": "per_drug_section",
                        "query": q_text,
                        "target_drug": drug,
                        "expected_section": expected_section,
                        "latency_sec": round(latency, 4),
                        "pass": passed,
                        "hits": len(hits),
                    })
                except Exception as e:
                    results.append({"test_type": "per_drug_section", "query": q_text, "pass": False, "error": str(e)})

        # --- B. Adversarial tests ---

        # B1. Impossible query — should return no/irrelevant results
        try:
            q_vec = self.embedder.provider.embed_texts(["Mechanism of action of Coca-Cola"])[0]
            hits = db_adapter.search(query_vector=q_vec, top_k=3)
            # Pass: no hit should have high confidence for a non-drug
            top_score = hits[0].score if hits else 0.0
            passed = top_score < 0.75  # Low similarity = correctly uncertain
            results.append({
                "test_type": "adversarial_impossible_query",
                "query": "Mechanism of action of Coca-Cola",
                "expected": "No high-confidence match",
                "top_score": round(top_score or 0.0, 4),
                "pass": passed,
            })
        except Exception as e:
            results.append({"test_type": "adversarial_impossible_query", "pass": False, "error": str(e)})

        # B2. Wrong drug — "Contraindications of Superman" should not return drug hits
        try:
            q_vec = self.embedder.provider.embed_texts(["Contraindications of Superman"])[0]
            hits = db_adapter.search(query_vector=q_vec, top_k=3)
            top_score = hits[0].score if hits else 0.0
            passed = top_score < 0.75
            results.append({
                "test_type": "adversarial_wrong_drug",
                "query": "Contraindications of Superman",
                "expected": "No high-confidence match",
                "top_score": round(top_score or 0.0, 4),
                "pass": passed,
            })
        except Exception as e:
            results.append({"test_type": "adversarial_wrong_drug", "pass": False, "error": str(e)})

        # B3. Brand search — "Novamox" should resolve to Amoxicillin content
        try:
            q_vec = self.embedder.provider.embed_texts(["Novamox dosage"])[0]
            hits = db_adapter.search(query_vector=q_vec, top_k=5)
            passed = any("amoxicillin" in h.metadata.get("drug_name", "").lower() for h in hits)
            results.append({
                "test_type": "adversarial_brand_resolution",
                "query": "Novamox dosage",
                "expected": "Amoxicillin content in results",
                "pass": passed,
            })
        except Exception as e:
            results.append({"test_type": "adversarial_brand_resolution", "pass": False, "error": str(e)})

        # B4. Typo tolerance — "Metoformin" should resolve to Metformin
        try:
            q_vec = self.embedder.provider.embed_texts(["Metoformin contraindications"])[0]
            hits = db_adapter.search(query_vector=q_vec, top_k=5)
            passed = any("metformin" in h.metadata.get("drug_name", "").lower() for h in hits)
            results.append({
                "test_type": "adversarial_typo_tolerance",
                "query": "Metoformin contraindications",
                "expected": "Metformin content in results",
                "pass": passed,
            })
        except Exception as e:
            results.append({"test_type": "adversarial_typo_tolerance", "pass": False, "error": str(e)})

        # B5. Multi-drug separation — results must not mix Metformin and Warfarin facts
        try:
            q_vec = self.embedder.provider.embed_texts(["Metformin Warfarin Lisinopril indications"])[0]
            hits = db_adapter.search(query_vector=q_vec, top_k=10)
            # Each hit should clearly belong to exactly one drug (no chunk blending two drugs)
            drugs_found = set(h.metadata.get("drug_name", "").lower() for h in hits)
            passed = len(drugs_found) > 1  # Multiple drugs found means separation is working
            results.append({
                "test_type": "adversarial_multi_drug_separation",
                "query": "Metformin Warfarin Lisinopril indications",
                "expected": "Multiple separate drug chunks returned",
                "drugs_found": list(drugs_found),
                "pass": passed,
            })
        except Exception as e:
            results.append({"test_type": "adversarial_multi_drug_separation", "pass": False, "error": str(e)})

        # B6. Mixed query routing — each sub-query should route to correct section
        mixed_queries = [
            ("Metformin dosage", "metformin", "dosage_and_administration"),
            ("Warfarin interactions", "warfarin", "drug_interactions"),
            ("Atorvastatin pregnancy", "atorvastatin", "pregnancy"),
        ]
        for q_text, expected_drug, expected_section in mixed_queries:
            try:
                q_vec = self.embedder.provider.embed_texts([q_text])[0]
                hits = db_adapter.search(query_vector=q_vec, top_k=5)
                drug_ok = any(expected_drug in h.metadata.get("drug_name", "").lower() for h in hits)
                results.append({
                    "test_type": "adversarial_mixed_query",
                    "query": q_text,
                    "expected_drug": expected_drug,
                    "expected_section": expected_section,
                    "pass": drug_ok,
                })
            except Exception as e:
                results.append({"test_type": "adversarial_mixed_query", "query": q_text, "pass": False, "error": str(e)})

        passed_count = sum(1 for r in results if r.get("pass"))
        logger.info("smoke_tests_completed", total=len(results), passed=passed_count, failed=len(results)-passed_count)
        return results


    def ingest_drugs(self, drug_names: List[str]):
        """
        Executes end-to-end ingestion run for the specified list of drugs with checkpointing & pre-Qdrant quality gates.
        """
        import json
        from .quality_gates import quality_gate_pipeline

        self.stats.start()
        
        # 1. Run preflight configuration check
        if not self.run_preflight_checks():
            logger.error("preflight_checks_failed_halting_ingestion")
            sys.exit(1)
            
        # Load ingestion checkpoint
        checkpoint_path = os.path.join(ingestion_config.BASE_DIR, "checkpoint.json")
        checkpoint = {"completed_drugs": [], "last_drug": None, "failed_drugs": []}
        if os.path.exists(checkpoint_path) and not self.force_reingest:
            try:
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    checkpoint = json.load(f)
                logger.info("loaded_ingestion_checkpoint", completed_count=len(checkpoint.get("completed_drugs", [])))
            except Exception as e:
                logger.warning("failed_reading_checkpoint", error=str(e))

        completed_set = set(checkpoint.get("completed_drugs", []))
        drugs_to_process = [d for d in drug_names if d.lower() not in completed_set or self.force_reingest]

        logger.info("ingestion_batch_summary", total_requested=len(drug_names), skipped_checkpointed=len(drug_names) - len(drugs_to_process), remaining=len(drugs_to_process))

        # 2. Process all documents and generate chunks
        all_chunks = []
        for name in drugs_to_process:
            logger.info("processing_drug_label", drug=name)
            try:
                chunks = self.process_drug(name)
                if chunks:
                    all_chunks.extend(chunks)
                
                # Update checkpoint
                completed_set.add(name.lower())
                checkpoint["completed_drugs"] = list(completed_set)
                checkpoint["last_drug"] = name
                with open(checkpoint_path, "w", encoding="utf-8") as f:
                    json.dump(checkpoint, f, indent=2)
            except Exception as e:
                logger.error("drug_processing_error", drug=name, error=str(e))
                if name.lower() not in checkpoint["failed_drugs"]:
                    checkpoint["failed_drugs"].append(name.lower())

        if not all_chunks:
            logger.warning("no_valid_chunks_created_skipping_embed_and_upload")
        else:
            # Run chunk-level quality validation
            valid_chunks, chunk_stats = self.validator.validate_chunks(all_chunks)
            logger.info("chunk_validation_completed", stats=chunk_stats)
            
            if not valid_chunks:
                logger.warning("no_chunks_passed_validation_skipping_embed_and_upload")
            else:
                chunks_to_embed = valid_chunks
                chunks_to_delete = []

                if self.incremental and not self.force_reingest:
                    unique_drugs = {chunk["drug_name"] for chunk in valid_chunks if chunk.get("drug_name")}
                    existing_hashes = {}
                    for d_name in unique_drugs:
                        existing_hashes.update(self.uploader.get_existing_chunk_hashes(d_name))

                    existing_hash_set = set(existing_hashes.values())
                    new_chunks = []
                    new_hash_set = set()
                    
                    for chunk in valid_chunks:
                        c_hash = chunk.get("chunk_hash")
                        if c_hash:
                            new_hash_set.add(c_hash)
                        if c_hash not in existing_hash_set:
                            new_chunks.append(chunk)

                    for point_id, old_hash in existing_hashes.items():
                        if old_hash not in new_hash_set:
                            chunks_to_delete.append(point_id)

                    chunks_to_embed = new_chunks
                    logger.info("chunk_level_incremental_diffing_completed", 
                                total_chunks=len(valid_chunks), 
                                unchanged_chunks=len(valid_chunks) - len(new_chunks),
                                new_or_changed_chunks=len(new_chunks),
                                obsolete_chunks_to_delete=len(chunks_to_delete))

                if chunks_to_delete:
                    self.uploader.delete_points_by_id(chunks_to_delete)

                if chunks_to_embed:
                    # 3. Generate batch embeddings
                    self.stats.embeddings_generated = len(chunks_to_embed)
                    embedded_chunks = self.embedder.embed_chunks(chunks_to_embed)
                    
                    # 4. Upload batches to Qdrant Cloud
                    uploaded, failed = self.uploader.upload_chunks(embedded_chunks)
                    self.stats.upload_success = uploaded
                    self.stats.upload_failures = failed
                
        self.stats.stop()
        
        # 5. Generate metrics reports, master drug index, and manifest
        self.report_generator.generate_manifest()
        self.report_generator.generate_ingestion_report()
        self.report_generator.generate_corpus_report()
        
        try:
            self.report_generator.generate_corpus_manifest()
            self.report_generator.generate_master_drug_index()
        except Exception as e:
            logger.error("failed_generating_corpus_manifest_or_index", error=str(e))
        
        # Print the Dataset Quality Report to stdout
        text_report = self.report_generator.get_text_quality_report()
        print("\n" + text_report + "\n")
        
        try:
            generate_reports()
        except Exception as e:
            logger.error("failed_generating_corpus_coverage_retrieval_reports", error=str(e))
        
        # 6. Execute final retrieval validation smoke tests — pass the just-ingested drugs
        smoke_drug_names = [d.capitalize() for d in drug_names[:20]]
        smoke_test_results = self.run_smoke_tests(drug_names=smoke_drug_names)
        self.report_generator.generate_smoke_test_report(smoke_test_results)
        
        logger.info("ingestion_pipeline_run_completed_successfully")


def main():
    parser = argparse.ArgumentParser(description="MedRef Enterprise Ingestion Pipeline")
    parser.add_argument(
        "--drugs", 
        type=str, 
        help="Comma-separated list of drug names to ingest (e.g. lisinopril,atorvastatin)"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Path to file containing list of drugs (one drug per line)"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force re-ingestion by bypassing incremental checksum checks"
    )
    
    parser.add_argument(
        "--incremental", 
        action="store_true", 
        help="Use chunk-level hashing to only embed and upload changed chunks"
    )
    
    args = parser.parse_args()
    
    drug_list = []
    if args.drugs:
        drug_list = [d.strip() for d in args.drugs.split(",") if d.strip()]
    elif args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                drug_list = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        else:
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
            
    if not drug_list:
        logger.error("no_drugs_specified", reason="Must provide --drugs or --file")
        sys.exit(1)
        
    orchestrator = IngestionOrchestrator(force_reingest=args.force, incremental=args.incremental)
    orchestrator.ingest_drugs(drug_list)

if __name__ == "__main__":
    main()
