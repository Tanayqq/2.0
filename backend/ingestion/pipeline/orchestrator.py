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
from app.infrastructure.vector_db import QdrantAdapter

logger = structlog.get_logger()

class IngestionOrchestrator:
    """
    Orchestrates the entire ingestion pipeline: health checks, collection,
    prioritization, parsing, validation, chunking, embedding, uploading,
    statistics collection, reporting, and retrieval smoke tests.
    """
    def __init__(self):
        self.stats = IngestionStatistics()
        self.parser = MedicalParser()
        self.validator = MedicalValidator()
        self.chunker = MedicalSectionChunker()
        self.embedder = MedicalEmbedder()
        self.uploader = MedicalUploader()
        self.report_generator = ReportGenerator(self.stats)
        
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
        
        logger.info("preflight_checks_passed_successfully")
        return True

    def merge_sources(self, docs_by_source: Dict[str, Any], drug_name: str) -> Optional[Any]:
        """
        Resolve source conflicts using the configured priority system.
        Keeps sections from the highest priority source, appending unique sections
        from lower priority sources to ensure maximum clinical coverage.
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
        
        if len(sorted_sources) == 1:
            return primary_doc
            
        # Merge sections from lower priority sources
        primary_section_titles = {sec.title.lower() for sec in primary_doc.sections}
        
        for other_source in sorted_sources[1:]:
            other_doc = docs_by_source[other_source]
            for sec in other_doc.sections:
                if sec.title.lower() not in primary_section_titles:
                    # Append unique clinical section
                    primary_doc.sections.append(sec)
                    primary_section_titles.add(sec.title.lower())
                    logger.info("merged_unique_section_from_lower_priority_source", 
                                drug=drug_name, section=sec.title, source=other_source)
                    
        return primary_doc

    def process_drug(self, drug_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch, prioritize, parse, validate, and chunk a single drug's labels.
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
            
        # 2. Conflict resolution via merge
        merged_doc = self.merge_sources(docs_by_source, drug_name)
        if not merged_doc:
            return None
            
        # 3. Clean and parse sections
        parsed_doc = self.parser.parse(merged_doc)
        
        # 4. Ingestion validation
        is_valid, reason = self.validator.validate(parsed_doc)
        if not is_valid:
            # Send failed record to Dead Letter Queue (DLQ) to ensure pipeline does not halt
            self.validator.send_to_dlq(parsed_doc, reason)
            self.stats.log_validation_failure(f"Validation failed for '{drug_name}': {reason}")
            return None
            
        self.stats.docs_parsed += 1
        self.stats.record_drug_sections(parsed_doc.drug, len(parsed_doc.sections))
        
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

    def run_smoke_tests(self) -> List[Dict[str, Any]]:
        """
        Execute smoke retrieval tests against Qdrant Cloud to verify the ingested database.
        """
        logger.info("running_retrieval_smoke_tests")
        
        # Instantiate adapter to connect directly to the target collection
        db_adapter = QdrantAdapter(
            url=ingestion_config.QDRANT_URL,
            api_key=ingestion_config.QDRANT_API_KEY,
            collection_name=ingestion_config.QDRANT_COLLECTION
        )
        
        smoke_queries = [
            {"query": "Contraindications of Metformin", "target_drug": "Metformin"},
            {"query": "Side effects of Atorvastatin", "target_drug": "Atorvastatin"},
            {"query": "Lisinopril warnings", "target_drug": "Lisinopril"},
            {"query": "Warfarin interactions", "target_drug": "Warfarin"},
            {"query": "Amoxicillin dosage", "target_drug": "Amoxicillin"},
            {"query": "Ibuprofen pregnancy", "target_drug": "Ibuprofen"},
            {"query": "Losartan contraindications", "target_drug": "Losartan"}
        ]
        
        results = []
        for item in smoke_queries:
            q_text = item["query"]
            target = item["target_drug"].lower()
            
            start_time = time.time()
            try:
                # Embed query text
                q_vec = self.embedder.provider.embed_texts([q_text])[0]
                # Search Qdrant
                hits = db_adapter.search(query_vector=q_vec, top_k=5)
                latency = time.time() - start_time
                
                # Check pass condition: top hit must relate to the target drug
                passed = False
                if hits:
                    top_hit = hits[0]
                    # Verify if target drug is mentioned in the top retrieved content
                    passed = target in top_hit.content.lower() or target in top_hit.metadata.get("drug", "").lower()
                    
                retrieved_chunks = [
                    {
                        "id": h.id,
                        "content": h.content,
                        "source": h.source,
                        "score": h.score or 0.0,
                        "metadata": h.metadata
                    }
                    for h in hits
                ]
                
                results.append({
                    "query": q_text,
                    "target_drug": item["target_drug"],
                    "latency_sec": latency,
                    "retrieved_chunks": retrieved_chunks,
                    "pass": passed
                })
                logger.info("smoke_test_query_executed", query=q_text, passed=passed, latency_sec=round(latency, 4))
                
            except Exception as e:
                logger.error("smoke_test_query_failed", query=q_text, error=str(e))
                results.append({
                    "query": q_text,
                    "target_drug": item["target_drug"],
                    "latency_sec": time.time() - start_time,
                    "retrieved_chunks": [],
                    "pass": False,
                    "error": str(e)
                })
                
        return results

    def ingest_drugs(self, drug_names: List[str]):
        """
        Executes end-to-end ingestion run for the specified list of drugs.
        """
        self.stats.start()
        
        # 1. Run preflight configuration check
        if not self.run_preflight_checks():
            logger.error("preflight_checks_failed_halting_ingestion")
            sys.exit(1)
            
        # 2. Process all documents and generate chunks
        all_chunks = []
        for name in drug_names:
            logger.info("processing_drug_label", drug=name)
            chunks = self.process_drug(name)
            if chunks:
                all_chunks.extend(chunks)
                
        if not all_chunks:
            logger.warning("no_valid_chunks_created_skipping_embed_and_upload")
        else:
            # Run chunk-level quality validation
            valid_chunks, chunk_stats = self.validator.validate_chunks(all_chunks)
            logger.info("chunk_validation_completed", stats=chunk_stats)
            
            if not valid_chunks:
                logger.warning("no_chunks_passed_validation_skipping_embed_and_upload")
            else:
                # 3. Generate batch embeddings
                self.stats.embeddings_generated = len(valid_chunks)
                embedded_chunks = self.embedder.embed_chunks(valid_chunks)
                
                # 4. Upload batches to Qdrant Cloud
                uploaded, failed = self.uploader.upload_chunks(embedded_chunks)
                self.stats.upload_success = uploaded
                self.stats.upload_failures = failed
                
        self.stats.stop()
        
        # 5. Generate metrics reports and manifest
        self.report_generator.generate_manifest()
        self.report_generator.generate_ingestion_report()
        self.report_generator.generate_corpus_report()
        
        try:
            generate_reports()
        except Exception as e:
            logger.error("failed_generating_corpus_coverage_retrieval_reports", error=str(e))
        
        # 6. Execute final retrieval validation smoke tests
        smoke_test_results = self.run_smoke_tests()
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
        # Default fallback list for smoke testing and MVP validation
        drug_list = ["lisinopril", "atorvastatin", "metformin", "amoxicillin", "ibuprofen", "losartan", "warfarin"]
        
    orchestrator = IngestionOrchestrator()
    orchestrator.ingest_drugs(drug_list)

if __name__ == "__main__":
    main()
