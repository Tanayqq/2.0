from typing import List, Tuple, Any, Dict
import time
import re
from app.domain.models import MedicalQuery, AnswerResponse, Citation, ReferenceDocument
from app.domain.interfaces import LLMProviderProtocol, VectorDatabaseProtocol, EmbeddingModelProtocol, CrossEncoderProtocol
from app.usecases.query_expansion import LayeredQueryExpander
from app.citation_map import CitationMap
from app.core.config import settings
from app.section_utils import normalize_section
from app.infrastructure.profile_store import StructuredProfileStore
import structlog

logger = structlog.get_logger()

SECTION_KEYWORDS = {
    "mechanism_of_action": ["mechanism of action", "mechanism", "pharmacological action"],
    "indications": ["indication", "indications", "indicated", "approved uses"],
    "clinical_pharmacology": ["clinical pharmacology", "pharmacology"],
    "pharmacokinetics": ["pharmacokinetics", "pharmacokinetic", "pk", "absorption", "distribution", "metabolism", "elimination"],
    "pharmacodynamics": ["pharmacodynamics", "pharmacodynamic"],
    "adverse_reactions": ["adverse reactions", "adverse reaction", "side effects", "side effect", "undesirable effects", "postmarketing", "clinical trials experience", "clinical studies experience"],
    "overdosage": ["overdosage", "overdose", "toxicity"],
    "storage": ["storage", "handling", "supplied", "store", "keep"],
    "patient_counseling": ["counseling", "patient counseling", "patient information", "information for patients"],
    "dosage_and_administration": ["dosage and administration", "dosage", "dosages", "dosing", "dose", "doses"],
    "administration": ["administration", "instructions for use", "how to administer"],
    "dosage_forms": ["dosage forms", "strengths", "dosage form"],
    "strengths": ["strengths", "strength"],
    "maximum_dose": ["maximum dose", "maximum dosage", "max dose"],
    "loading_dose": ["loading dose", "loading dosage"],
    "maintenance_dose": ["maintenance dose", "maintenance dosage"],
    "renal_dose": ["renal dose", "renal dosing", "dosage in renal impairment"],
    "hepatic_dose": ["hepatic dose", "hepatic dosing", "dosage in hepatic impairment"],
    "dose_adjustment": ["dose adjustment", "dosage adjustment", "dosage modifications", "dose modification", "adjustments"],
    "contraindications": ["contraindications", "contraindication", "contraindicated"],
    "boxed_warning": ["boxed warning", "boxed warnings", "black box warning", "black box"],
    "warnings": ["warnings", "warning"],
    "warnings_and_precautions": ["warnings and precautions", "warnings & precautions"],
    "precautions": ["precautions", "precaution"],
    "drug_interactions": ["drug interactions", "drug interaction", "drug-drug interactions", "interactions", "interaction"],
    "alcohol_interactions": ["alcohol interactions", "alcohol interaction", "interaction with alcohol"],
    "food_interactions": ["food interactions", "food interaction", "interaction with food"],
    "cyp_interactions": ["cyp interactions", "cyp interaction", "cytochrome p450"],
    "laboratory_interactions": ["laboratory interactions", "laboratory interaction", "drug and laboratory test interactions"],
    "monitoring": ["monitoring", "monitoring parameter", "patient monitoring", "therapeutic monitoring"],
    "pregnancy": ["pregnancy", "use in pregnancy", "pregnancy warning", "pregnant", "teratogenic", "fetus", "fetal"],
    "lactation": ["lactation", "nursing mothers", "breast-feeding mothers", "breastfeeding", "use in lactation", "nursing", "breast milk", "human milk"],
    "pediatric_use": ["pediatric use", "use in children", "pediatric", "children", "child", "infant", "infants"],
    "geriatric_use": ["geriatric use", "use in elderly", "use in geriatric patients", "geriatric", "elderly", "older patients"],
    "renal_impairment": ["renal impairment", "patients with renal impairment", "renal insufficiency"],
    "hepatic_impairment": ["hepatic impairment", "patients with hepatic impairment", "hepatic insufficiency"],
    "dialysis": ["dialysis", "hemodialysis"],
    "pharmacogenomics": ["pharmacogenomics", "pharmacogenomic", "genetics"]
}

# normalize_section_title_helper is a backward-compatible alias for the shared utility
normalize_section_title_helper = normalize_section

# ---------------------------------------------------------------------------
# Helper: resolve section name from any metadata key variant
# ---------------------------------------------------------------------------
_SECTION_KEYS = ("section", "Section", "category", "Category", "clinical_section", "sectionTitle")

def _resolve_raw_section(metadata: dict) -> str:
    """Read the raw section value from a Qdrant payload, trying multiple key variants."""
    for key in _SECTION_KEYS:
        val = metadata.get(key)
        if val and str(val).strip():
            return str(val).strip()
    return ""

def _build_db_filters(query, drug, detected_sections) -> dict:
    """
    Construct Qdrant payload filters supporting drug_name, canonical_section, source, and document_type.
    """
    db_filters = {}
    
    # 1. Map drug name/drug
    if drug:
        db_filters["drug_name"] = drug
        db_filters["drug"] = drug
        
    # 2. Map canonical_section/section
    section_filter_val = None
    if query.filters:
        section_filter_val = query.filters.get("canonical_section") or query.filters.get("section")
    if not section_filter_val and detected_sections:
        section_filter_val = detected_sections
        
    if section_filter_val:
        if not isinstance(section_filter_val, list):
            section_filter_val = [section_filter_val]
        # Include both canonical_section and section for compatibility
        db_filters["canonical_section"] = section_filter_val
        db_filters["section"] = section_filter_val

    # 3. Map source
    if query.filters and "source" in query.filters:
        db_filters["source"] = query.filters["source"]
        
    # 4. Map document_type
    if query.filters and "document_type" in query.filters:
        db_filters["document_type"] = query.filters["document_type"]
        db_filters["category"] = query.filters["document_type"]
        
    return db_filters

def safe_log_str(s: str) -> str:
    if not isinstance(s, str):
        return str(s)
    return s.encode('ascii', errors='replace').decode('ascii')

def _balance_by_section(docs: List[Any], requested_sections: List[str], max_total: int) -> List[Any]:
    """
    Diversify the retrieved chunks by ensuring at least the top chunk from each 
    requested section is selected, preventing a single high-scoring section 
    from dominating the context window.
    """
    if not requested_sections or not docs:
        return docs[:max_total]
        
    by_section = {sec: [] for sec in requested_sections}
    other_docs = []
    
    for d in docs:
        db_sec_raw = _resolve_raw_section(d.metadata)
        db_sec = normalize_section(db_sec_raw)
        if db_sec in by_section:
            by_section[db_sec].append(d)
        else:
            other_docs.append(d)
            
    # Sort each list by score descending
    for sec in requested_sections:
        by_section[sec].sort(key=lambda x: x.score or 0.0, reverse=True)
    other_docs.sort(key=lambda x: x.score or 0.0, reverse=True)
    
    selected = []
    added_uuids = set()
    
    # Step 1: Round-robin pick the top document from each requested section
    for sec in requested_sections:
        if by_section[sec]:
            doc = by_section[sec].pop(0)
            selected.append(doc)
            added_uuids.add(doc.id)
            if len(selected) >= max_total:
                break
                
    # Step 2: Fill remaining slots with the highest-scoring leftover documents
    if len(selected) < max_total:
        remaining_pool = []
        for sec in requested_sections:
            remaining_pool.extend(by_section[sec])
        remaining_pool.extend(other_docs)
        remaining_pool.sort(key=lambda x: x.score or 0.0, reverse=True)
        
        for doc in remaining_pool:
            if doc.id not in added_uuids:
                selected.append(doc)
                added_uuids.add(doc.id)
                if len(selected) >= max_total:
                    break
                    
    return selected

class ProcessClinicalQueryUseCase:
    def __init__(
        self, 
        llm_provider: LLMProviderProtocol, 
        vector_db: VectorDatabaseProtocol, 
        embedding_model: EmbeddingModelProtocol,
        cross_encoder: CrossEncoderProtocol
    ):
        self.llm = llm_provider
        self.vector_db = vector_db
        self.embedding = embedding_model
        self.cross_encoder = cross_encoder
        self.expander = LayeredQueryExpander()
        self.prompt_version = "v2.0-hybrid-reranked"
        
        self.profile_store = StructuredProfileStore()
        try:
            self.profile_store.load_aliases_cache()
        except Exception as e:
            logger.warning("failed_preloading_aliases_cache_during_init", error=str(e))

    def _build_context(self, query: MedicalQuery) -> Tuple[str, List[Citation], List[Any], float, str, Dict[str, Any]]:
        start_retrieve = time.time()
        
        # 1. Resolve drug name using StructuredProfileStore and DrugNameResolver
        from app.usecases.drug_resolver import DrugNameResolver
        
        detected_drugs = []
        words = [w.strip("?,.:;!\"'()[]{}").lower() for w in query.question.split()]
        for word in words:
            # 1a. Try StructuredProfileStore aliases cache
            resolved_entity = self.profile_store.get_entity_by_alias(word)
            if resolved_entity:
                generic = resolved_entity.split(":")[-1]
                detected_drugs.append(generic)
                continue
                
            # 1b. Fallback to DrugNameResolver
            if word in DrugNameResolver.GENERIC_NAMES:
                detected_drugs.append(word)
            elif word in DrugNameResolver.BRAND_TO_GENERIC:
                detected_drugs.append(DrugNameResolver.BRAND_TO_GENERIC[word])
                
        # Substring checks
        query_lower = query.question.lower()
        for word in query_lower.split():
            resolved_entity = self.profile_store.get_entity_by_alias(word)
            if resolved_entity:
                generic = resolved_entity.split(":")[-1]
                detected_drugs.append(generic)
                
        for generic in DrugNameResolver.GENERIC_NAMES:
            if generic in query_lower:
                detected_drugs.append(generic)
        for brand, generic in DrugNameResolver.BRAND_TO_GENERIC.items():
            if brand in query_lower:
                detected_drugs.append(generic)
                
        detected_drugs = list(set(detected_drugs))
        
        if "unfound" in detected_drugs:
            return "", [], [], 0.0, "Low", {
                "retrieval_latency_sec": 0.0,
                "total_retrieved": 0,
                "total_filtered": 0,
                "threshold_applied": 0.0,
                "status": "unfound_drug_fast_path"
            }
            
        if detected_drugs and len(detected_drugs) > 1:
            resolved_drug = [d.capitalize() for d in detected_drugs]
        elif detected_drugs:
            resolved_drug = detected_drugs[0].capitalize()
        else:
            resolved_drug = None
        
        # 2. Detect requested clinical sections (negation-aware to ignore "Do not include X")
        q_lower = query.question.lower()
        detected_sections = []
        import re
        
        def is_negated(text: str, keyword: str) -> bool:
            # Match negation words before the keyword in the same sentence/phrase (prevent matching across lines)
            negation_pattern = r'\b(do not|don\'t|never|excluding|except|omit|without|no|other than|except for|avoid)\b[^.!?\n]*?\b' + re.escape(keyword) + r'\b'
            return bool(re.search(negation_pattern, text, re.IGNORECASE))
            
        for canonical_sec, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                    if not is_negated(q_lower, kw):
                        detected_sections.append(canonical_sec)
                        break
        detected_sections = list(set(detected_sections))

        # Expand detected sections to cover related canonical keys in their clinical categories
        def expand_sections(detected: list[str]) -> list[str]:
            expanded = set(detected)
            groups = {
                "warnings": ["warnings", "warnings_and_precautions", "boxed_warning", "precautions"],
                "warnings_and_precautions": ["warnings", "warnings_and_precautions", "boxed_warning", "precautions"],
                "precautions": ["warnings", "warnings_and_precautions", "boxed_warning", "precautions"],
                "boxed_warning": ["warnings", "warnings_and_precautions", "boxed_warning", "precautions"],
                "drug_interactions": ["drug_interactions", "alcohol_interactions", "food_interactions", "cyp_interactions", "laboratory_interactions", "monitoring"],
                "dosage_and_administration": ["dosage_and_administration", "administration", "dosage_forms", "strengths", "maximum_dose", "loading_dose", "maintenance_dose", "renal_dose", "hepatic_dose", "dose_adjustment"],
                "dosage": ["dosage_and_administration", "administration", "dosage_forms", "strengths", "maximum_dose", "loading_dose", "maintenance_dose", "renal_dose", "hepatic_dose", "dose_adjustment"],
                "pregnancy": ["pregnancy", "lactation"],
                "lactation": ["pregnancy", "lactation"],
                "renal_impairment": ["renal_impairment", "renal_dose", "dialysis"],
                "hepatic_impairment": ["hepatic_impairment", "hepatic_dose"]
            }
            for item in detected:
                if item in groups:
                    expanded.update(groups[item])
            return list(expanded)
            
        detected_sections = expand_sections(detected_sections)
        
        # If no sections are detected (e.g. general drug query), default to all canonical sections
        # to ensure we pull chunks for the complete clinical report categories
        if not detected_sections:
            detected_sections = list(SECTION_KEYWORDS.keys())
        
        logger.info(
            "section_detection",
            question=query.question,
            detected_drug=resolved_drug,
            detected_sections=detected_sections
        )
        if not detected_sections:
            logger.warning("no_sections_detected", question=query.question)
        
        rejection_log = []
        raw_retrieved_log = []
        
        # Determine Top-K retrieval depth
        is_default_all = len(detected_sections) > 30
        top_k_to_request = 100 if is_default_all else (settings.MULTI_SECTION_TOP_K if len(detected_sections) > 0 else settings.DEFAULT_TOP_K)
        
        # 3. Query Expansion (Ontology -> LLM)
        expanded_queries = self.expander.expand(query.question, skip_llm=(resolved_drug is not None))
        
        total_retrieved = 0
        total_filtered = 0
        
        # 4. Search and retrieve documents
        if resolved_drug and isinstance(resolved_drug, list):
            # For multiple drugs, run separate searches for each drug to avoid imbalanced dominance
            all_retrieved_docs_by_drug = []
            for drug in resolved_drug:
                drug_retrieved: dict[str, ReferenceDocument] = {}
                for q in expanded_queries:
                    dense_vec = self.embedding.embed_query(q)
                    sparse_vec = self.embedding.embed_sparse(q)
                    
                    db_filters = _build_db_filters(query, drug, detected_sections)
                    
                    if sparse_vec:
                        docs = self.vector_db.hybrid_search(
                            dense_vector=dense_vec,
                            sparse_vector=sparse_vec,
                            top_k=top_k_to_request,
                            filters=db_filters
                        )
                    else:
                        docs = self.vector_db.search(
                            query_vector=dense_vec,
                            top_k=top_k_to_request,
                            filters=db_filters
                        )
                    total_retrieved += len(docs)
                    for doc in docs:
                        drug_retrieved[doc.id] = doc
                        raw_retrieved_log.append(f"UUID: {doc.id}, Score: {round(doc.score or 0.0, 4)}, Drug: {doc.metadata.get('drug_name', doc.metadata.get('drug', ''))}, Section: {doc.metadata.get('section', '')}")
                
                # Sort and prioritize for this drug
                drug_docs = list(drug_retrieved.values())
                drug_docs.sort(key=lambda x: x.score or 0.0, reverse=True)
                
                if detected_sections:
                    in_section = []
                    filter_trace = []
                    for d in drug_docs:
                        db_sec_raw = _resolve_raw_section(d.metadata)
                        db_sec = normalize_section(db_sec_raw)
                        decision = "PASS" if db_sec in detected_sections else "DROP"
                        filter_trace.append({
                            "uuid": d.id,
                            "raw_section": db_sec_raw,
                            "normalized_section": db_sec,
                            "requested": detected_sections,
                            "decision": decision,
                            "score": round(d.score or 0.0, 4)
                        })
                        if decision == "PASS":
                            in_section.append(d)
                        else:
                            rejection_log.append(
                                f"DROP {d.id} (score={round(d.score or 0.0, 4)}) "
                                f"raw='{db_sec_raw}' normalized='{db_sec}' "
                                f"requested={detected_sections}"
                            )
                    
                    logger.info(
                        "section_filter_multidrug",
                        drug=drug,
                        retrieved=len(drug_docs),
                        passed=len(in_section),
                        dropped=len(drug_docs) - len(in_section),
                        requested_sections=detected_sections,
                        filter_trace=filter_trace
                    )
                    
                    drug_docs = in_section
                
                threshold = settings.SIMILARITY_THRESHOLD
                drug_threshold_docs = [d for d in drug_docs if (d.score or 0.0) >= threshold]
                if not drug_threshold_docs and drug_docs:
                    drug_threshold_docs = [d for d in drug_docs if (d.score or 0.0) >= 0.35]
                    
                for d in drug_docs:
                    if d not in drug_threshold_docs:
                        rejection_log.append(f"Rejected {d.id} (Score {round(d.score or 0.0, 4)}): Below similarity threshold {threshold}")
                
                total_filtered += len(drug_threshold_docs)
                # Keep top 3 for this drug to guarantee balance, diversified by section!
                # Dynamic chunk budget: 1 chunk per requested section (minimum), not a fixed number
                per_drug_budget = max(len(detected_sections), 3)
                diversified_drug_docs = _balance_by_section(drug_threshold_docs, detected_sections, max_total=per_drug_budget)
                all_retrieved_docs_by_drug.extend(diversified_drug_docs)
            
            final_docs = all_retrieved_docs_by_drug
        else:
            # Single drug or no resolved drug
            all_retrieved_docs: dict[str, ReferenceDocument] = {}
            for q in expanded_queries:
                dense_vec = self.embedding.embed_query(q)
                sparse_vec = self.embedding.embed_sparse(q)
                
                db_filters = _build_db_filters(query, resolved_drug, detected_sections)
                
                if sparse_vec:
                    docs = self.vector_db.hybrid_search(
                        dense_vector=dense_vec,
                        sparse_vector=sparse_vec,
                        top_k=top_k_to_request,
                        filters=db_filters
                    )
                else:
                    docs = self.vector_db.search(
                        query_vector=dense_vec,
                        top_k=top_k_to_request,
                        filters=db_filters
                    )
                total_retrieved += len(docs)
                for doc in docs:
                    all_retrieved_docs[doc.id] = doc
                    raw_retrieved_log.append(f"UUID: {doc.id}, Score: {round(doc.score or 0.0, 4)}, Drug: {doc.metadata.get('drug_name', doc.metadata.get('drug', ''))}, Section: {doc.metadata.get('section', '')}")
                    
            merged_docs = list(all_retrieved_docs.values())
            merged_docs.sort(key=lambda x: x.score or 0.0, reverse=True)
            
            filtered_docs = merged_docs
            if resolved_drug:
                # Extra precaution to filter by resolved drug
                filtered_docs = [
                    d for d in filtered_docs
                    if d.metadata.get("drug", "").lower() == resolved_drug.lower() or
                       d.metadata.get("drug_name", "").lower() == resolved_drug.lower()
                ]
            else:
                # Strict check: if no drug is resolved, we must only keep documents
                # whose drug name (generic or brand) is explicitly mentioned in the query text.
                # This prevents leaks of unrelated drugs (like 'Antigravity' returning 'Ciprofloxacin').
                from app.usecases.drug_resolver import DrugNameResolver
                
                def is_doc_drug_mentioned(doc) -> bool:
                    doc_drug = doc.metadata.get("drug", doc.metadata.get("drug_name", ""))
                    if not doc_drug:
                        return True
                    doc_drug_lower = doc_drug.lower()
                    query_lower = query.question.lower()
                    if doc_drug_lower in query_lower:
                        return True
                    for brand, generic in DrugNameResolver.BRAND_TO_GENERIC.items():
                        if generic == doc_drug_lower and brand in query_lower:
                            return True
                    return False
                
                filtered_docs = [d for d in filtered_docs if is_doc_drug_mentioned(d)]
                
            if detected_sections:
                in_section = []
                filter_trace = []
                for d in filtered_docs:
                    db_sec_raw = _resolve_raw_section(d.metadata)
                    db_sec = normalize_section(db_sec_raw)
                    decision = "PASS" if db_sec in detected_sections else "DROP"
                    filter_trace.append({
                        "uuid": d.id,
                        "raw_section": db_sec_raw,
                        "normalized_section": db_sec,
                        "requested": detected_sections,
                        "decision": decision,
                        "score": round(d.score or 0.0, 4)
                    })
                    if decision == "PASS":
                        in_section.append(d)
                    else:
                        rejection_log.append(
                            f"DROP {d.id} (score={round(d.score or 0.0, 4)}) "
                            f"raw='{db_sec_raw}' normalized='{db_sec}' "
                            f"requested={detected_sections}"
                        )
                
                logger.info(
                    "section_filter",
                    retrieved=len(filtered_docs),
                    passed=len(in_section),
                    dropped=len(filtered_docs) - len(in_section),
                    requested_sections=detected_sections,
                    filter_trace=filter_trace
                )
                
                filtered_docs = in_section
                
            threshold = settings.SIMILARITY_THRESHOLD
            threshold_filtered_docs = [d for d in filtered_docs if (d.score or 0.0) >= threshold]
            if not threshold_filtered_docs and filtered_docs:
                threshold_filtered_docs = [d for d in filtered_docs if (d.score or 0.0) >= 0.35]
                
            for d in filtered_docs:
                if d not in threshold_filtered_docs:
                    rejection_log.append(f"Rejected {d.id} (Score {round(d.score or 0.0, 4)}): Below similarity threshold {threshold}")
                    
            total_filtered += len(threshold_filtered_docs)
            is_multi_section = len(detected_sections) > 5
            max_chunks_budget = 15 if is_multi_section else settings.MAX_CONTEXT_CHUNKS
            final_docs = _balance_by_section(threshold_filtered_docs, detected_sections, max_total=max_chunks_budget)
            
        retrieve_time = time.time() - start_retrieve
        
        # 6. Calculate Confidence
        avg_similarity = sum(d.score or 0.0 for d in final_docs) / len(final_docs) if final_docs else 0.0
        
        if avg_similarity >= 0.82:
            confidence = "High"
        elif avg_similarity >= 0.72:
            confidence = "Medium"
        else:
            confidence = "Low"
            
        if len(final_docs) < 3:
            if confidence == "High":
                confidence = "Medium"
            elif confidence == "Medium":
                confidence = "Low"
                
        if resolved_drug and not final_docs:
            confidence = "Low"
            
        # Deduplicate final_docs by UUID to ensure no duplicate entries exist in the bibliography
        seen_uuids = set()
        deduped_final_docs = []
        for doc in final_docs:
            if doc.id not in seen_uuids:
                seen_uuids.add(doc.id)
                deduped_final_docs.append(doc)
        final_docs = deduped_final_docs

        # 7. Assign sequential citation IDs and build STRUCTURED context (grouped by Drug → Section)
        from app.preprocessor import clean_chunk_content
        
        citation_map = CitationMap()
        citations = []
        citation_counter = 0
        uuid_to_citation_id = {}
        
        # Organize docs by (drug, clinical_category)
        from app.section_utils import get_clinical_category
        
        docs_by_drug_category: Dict[str, Dict[str, list]] = {}
        for doc in final_docs:
            drug = doc.metadata.get('drug_name', doc.metadata.get('drug', ''))
            raw_sec = _resolve_raw_section(doc.metadata)
            norm_sec = normalize_section(raw_sec)
            clinical_cat = doc.metadata.get('clinical_category', get_clinical_category(norm_sec))
            
            if drug not in docs_by_drug_category:
                docs_by_drug_category[drug] = {}
            if clinical_cat not in docs_by_drug_category[drug]:
                docs_by_drug_category[drug][clinical_cat] = []
            docs_by_drug_category[drug][clinical_cat].append(doc)
        
        # Determine the list of drugs (preserve order from resolved_drug or from docs)
        if resolved_drug and isinstance(resolved_drug, list):
            drug_order = resolved_drug
        elif resolved_drug:
            drug_order = [resolved_drug]
        else:
            drug_order = list(docs_by_drug_category.keys())
        
        # Log per-drug per-category chunk counts
        coverage_log = {}
        detected_categories = list(set(get_clinical_category(sec) for sec in (detected_sections if detected_sections else [])))
        for drug in drug_order:
            coverage_log[drug] = {}
            for cat in (detected_categories if detected_categories else ["_all"]):
                count = len(docs_by_drug_category.get(drug, {}).get(cat, []))
                coverage_log[drug][cat] = count
        
        logger.info(
            "retrieval_coverage",
            drugs=drug_order,
            detected_sections=detected_sections,
            detected_categories=detected_categories,
            per_drug_per_category=coverage_log
        )
        
        # Build structured context string (with strict size limit to stay under Groq rate limits)
        context_str = ""
        max_char_limit = 18000
        
        for drug in drug_order:
            if len(context_str) >= max_char_limit:
                break
                
            drug_str = ""
            drug_str += f"{'='*60}\n"
            drug_str += f"DRUG: {drug}\n"
            drug_str += f"{'='*60}\n\n"
            
            categories_to_render = detected_categories if detected_categories else list(docs_by_drug_category.get(drug, {}).keys())
            
            for cat in categories_to_render:
                if len(context_str) + len(drug_str) >= max_char_limit:
                    break
                    
                cat_str = ""
                cat_str += f"--- Category: {cat} ---\n\n"
                
                cat_docs = docs_by_drug_category.get(drug, {}).get(cat, [])
                
                if not cat_docs:
                    cat_str += "NO DOCUMENTS AVAILABLE FOR THIS CATEGORY.\n\n"
                    drug_str += cat_str
                    continue
                
                for doc in cat_docs:
                    if len(context_str) + len(drug_str) + len(cat_str) >= max_char_limit:
                        break
                        
                    # Re-use existing citation ID if chunk UUID has been cited before
                    if doc.id in uuid_to_citation_id:
                        citation_id = uuid_to_citation_id[doc.id]
                        is_new_citation = False
                    else:
                        citation_counter += 1
                        citation_id = str(citation_counter)
                        uuid_to_citation_id[doc.id] = citation_id
                        is_new_citation = True
                        
                    section_raw = doc.metadata.get('section', doc.metadata.get('category', ''))
                    cleaned_content = clean_chunk_content(doc.content)
                    
                    doc_str = ""
                    doc_str += f"DOCUMENT {citation_id}\n"
                    doc_str += f"Citation Number: [{citation_id}]\n"
                    doc_str += f"Source: {doc.source}\n"
                    doc_str += f"Section: {section_raw}\n"
                    doc_str += f"Facts:\n"
                    for line in cleaned_content.split('\n'):
                        if line.strip():
                            doc_str += f"{line}\n"
                    doc_str += f"\n"
                    
                    cat_str += doc_str
                    
                    if is_new_citation:
                        # Add to citation map
                        citation_map.add_entry(
                            uuid=doc.id,
                            citation_number=citation_id,
                            source=doc.source,
                            drug=drug,
                            section=section_raw,
                            text=cleaned_content,
                            similarity=round(doc.score or 0.0, 4)
                        )
                        
                        # Add to citations list
                        citations.append(Citation(
                            document_id=citation_id,
                            source=f"{doc.source} – {drug} – {section_raw}",
                            snippet=cleaned_content,
                            uuid=doc.id,
                            drug=drug,
                            section=section_raw,
                            similarity=round(doc.score or 0.0, 4),
                            count=0
                        ))
                    
                drug_str += cat_str
            
            context_str += drug_str + "\n"
            
        retrieval_stats = {
            "rank_scores": [round(d.score or 0.0, 4) for d in final_docs],
            "retrieval_latency_sec": round(retrieve_time, 4),
            "total_retrieved": total_retrieved,
            "total_filtered": total_filtered,
            "threshold_applied": threshold,
            "confidence": confidence,
            "avg_similarity": round(avg_similarity, 4),
            "retrieved_count": len(final_docs),
            "resolved_drug": resolved_drug,
            "detected_sections": detected_sections,
            "raw_retrieved_log": raw_retrieved_log,
            "rejection_log": rejection_log,
            "coverage": coverage_log
        }
        
        return context_str, citations, final_docs, retrieve_time, confidence, retrieval_stats, citation_map

    def _build_prompt(self, context_str: str, question: str) -> str:
        return f"""
Context:
{context_str}

Question: {question}

You are a clinical evidence extraction engine. You extract facts ONLY from the DOCUMENTS above.

CRITICAL RULES:

1. CITATIONS ARE MANDATORY.
   After EVERY factual sentence, you MUST append the citation number in square brackets.
   CORRECT: "Metformin is contraindicated in severe renal impairment.[1]"
   CORRECT: "Warfarin may increase the risk of bleeding.[3]"
   WRONG:   "Metformin is contraindicated in severe renal impairment."
   WRONG:   "Warfarin may increase the risk of bleeding."
   A sentence without a citation number is INVALID and will be removed.

2. CONCISE SUMMARY ONLY.
   You MUST summarize the retrieved clinical evidence concisely instead of dumping long verbatim FDA excerpts.
   However, every single sentence you write MUST be strictly grounded in the facts from the DOCUMENTS above.
   Do NOT paraphrase loosely or extrapolate beyond the provided documents.
   Do NOT invent drug interactions, contraindications, or warnings.

3. SECTION BOUNDARIES ARE ABSOLUTE.
   The context is organized by Drug and Clinical Category / Section.
   - If a category or section says "NO DOCUMENTS AVAILABLE", you MUST respond with exactly:
     Not found in available sources.
   - NEVER use a "drug interactions" document to answer a "Contraindications" question.
   - NEVER use a "warnings" document to answer a "Drug Interactions" question.
   - Each section's answer must come ONLY from documents under that same category or section.

4. NEVER MIX DRUGS.
   Facts about Metformin must NEVER appear under Warfarin's section, and vice versa.

5. NEVER generate from memory.
   If no DOCUMENT exists for a requested fact, do NOT write it.
   Prefer "Not found in available sources." over any invented statement.

6. Do NOT output FDA cross-references like "[see Warnings and Precautions (5.1)]".
   Do NOT invent citation numbers that don't exist in the DOCUMENTS.

7. ABSOLUTELY NO DEBUG/DOCUMENT LABEL ARTIFACTS.
   Never include text like "DOCUMENT 1", "DOCUMENT 2", or "Source: ..." in your final answers.
   Only output the clean, structured clinical report text with inline citations.

8. STRICT OUTPUT FORMAT:
   You MUST format your response as a structured markdown report for EACH drug. Use the following exact headers for each drug and section, with no extra text outside this format:

   ### [Drug Name]

   #### Clinical Profile Overview
   [Insert facts or "Not found in available sources."]

   #### Dosing & Administration
   [Insert facts or "Not found in available sources."]

   #### Contraindications
   [Insert facts or "Not found in available sources."]

   #### Warnings
   [Insert facts or "Not found in available sources."]

   #### Co-Administration Risks
   [Insert facts or "Not found in available sources."]
"""

    def get_debug_retrieval(self, query: MedicalQuery):
        """Expanded debug endpoint: returns all raw pre-filter data + filter trace."""
        # Run retrieval (which now includes instrumented filter_trace in rejection_log)
        _, _, documents, total_retrieval_time, confidence, retrieval_stats, _ = self._build_context(query)
        
        # Also do a raw unfiltered search so the caller can see what Qdrant returned before filtering
        from app.usecases.drug_resolver import DrugNameResolver
        q_lower = query.question.lower()
        
        # Drug resolution (duplicate minimal version for debug only)
        detected_drugs_debug = []
        for generic in DrugNameResolver.GENERIC_NAMES:
            if generic in q_lower:
                detected_drugs_debug.append(generic)
        for brand, generic in DrugNameResolver.BRAND_TO_GENERIC.items():
            if brand in q_lower:
                detected_drugs_debug.append(generic)
        detected_drugs_debug = list(set(detected_drugs_debug))
        resolved_drug_debug = detected_drugs_debug[0].capitalize() if detected_drugs_debug else None
        
        # Section detection (same logic, negation-aware)
        import re as _re
        detected_sections_debug = []
        def is_negated_debug(text: str, keyword: str) -> bool:
            negation_pattern = r'\b(do not|don\'t|never|excluding|except|omit|without|no|other than|except for|avoid)\b[^.!?]*?\b' + _re.escape(keyword) + r'\b'
            return bool(_re.search(negation_pattern, text, _re.IGNORECASE))
            
        for canonical_sec, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if _re.search(r'\b' + _re.escape(kw) + r'\b', q_lower):
                    if not is_negated_debug(q_lower, kw):
                        detected_sections_debug.append(canonical_sec)
                        break
        detected_sections_debug = list(set(detected_sections_debug))
        
        # Raw Qdrant search (no section filter)
        dense_vec = self.embedding.embed_query(query.question)
        sparse_vec = self.embedding.embed_sparse(query.question)
        db_filters_raw = {}
        if resolved_drug_debug:
            db_filters_raw["drug"] = resolved_drug_debug
        top_k = getattr(settings, "MULTI_SECTION_TOP_K", 30)
        try:
            if sparse_vec:
                raw_docs = self.vector_db.hybrid_search(
                    dense_vector=dense_vec,
                    sparse_vector=sparse_vec,
                    top_k=top_k,
                    filters=db_filters_raw
                )
            else:
                raw_docs = self.vector_db.search(
                    query_vector=dense_vec,
                    top_k=top_k,
                    filters=db_filters_raw
                )
        except Exception as e:
            raw_docs = []
            logger.error("debug_raw_search_failed", error=str(e))
        
        # Build filter trace for every raw doc
        filter_trace = []
        for doc in raw_docs:
            raw_sec = _resolve_raw_section(doc.metadata)
            norm_sec = normalize_section(raw_sec)
            passes = norm_sec in detected_sections_debug if detected_sections_debug else True
            filter_trace.append({
                "uuid": doc.id,
                "drug_name": doc.metadata.get("drug_name", doc.metadata.get("drug", "")),
                "generic_name": doc.metadata.get("generic_name", ""),
                "raw_section": raw_sec,
                "normalized_section": norm_sec,
                "source": doc.metadata.get("source", ""),
                "score": round(doc.score or 0.0, 4),
                "passes_section_filter": passes,
                "decision": "PASS" if passes else "DROP"
            })
        
        passed_count = sum(1 for t in filter_trace if t["passes_section_filter"])
        dropped_count = len(filter_trace) - passed_count
        
        return {
            "debug_summary": {
                "detected_drug": resolved_drug_debug,
                "detected_sections": detected_sections_debug,
                "raw_retrieved_count": len(raw_docs),
                "passed_filter_count": passed_count,
                "dropped_filter_count": dropped_count,
                "final_context_chunks": len(documents)
            },
            "filter_trace": filter_trace,
            "final_chunks_after_filter": [
                {
                    "uuid": doc.id,
                    "score": doc.score,
                    "drug": doc.metadata.get("drug_name", doc.metadata.get("drug", "")),
                    "section": _resolve_raw_section(doc.metadata),
                    "normalized_section": normalize_section(_resolve_raw_section(doc.metadata)),
                    "source": doc.source,
                    "chunk_length": len(doc.content),
                    "rank": i + 1
                }
                for i, doc in enumerate(documents)
            ],
            "retrieval_time_sec": round(total_retrieval_time, 4),
            "metrics": {
                "retrieval_latency_sec": retrieval_stats["retrieval_latency_sec"],
                "total_retrieved": retrieval_stats["total_retrieved"],
                "total_filtered": retrieval_stats["total_filtered"],
                "threshold_applied": retrieval_stats["threshold_applied"],
                "confidence": confidence,
                "raw_retrieved_log": retrieval_stats.get("raw_retrieved_log", []),
                "rejection_log": retrieval_stats.get("rejection_log", [])
            }
        }
        
    def get_debug_prompt(self, query: MedicalQuery):
        context_str, _, _, _, _, _, _ = self._build_context(query)
        prompt = self._build_prompt(context_str, query.question)
        return {
            "prompt_version": self.prompt_version,
            "provider": settings.ACTIVE_LLM_PROVIDER,
            "generated_prompt": prompt
        }

    def _post_process_and_validate(
        self, 
        answer_text: str, 
        citations: List[Citation], 
        citation_map: CitationMap
    ) -> Tuple[str, List[Citation], Dict[str, str], List[str]]:
        import re as regex
        
        if answer_text.strip().strip(".!").lower() == "not found in available sources":
            return "Not found in available sources.", [], {}, []
            
        # 0. Strip raw text bibliography generated by the LLM (to avoid duplicating it)
        bib_indicators = [
            r'\n\s*Sources\s+Referenced\s*:',
            r'\n\s*References\s*:',
            r'\n\s*Bibliography\s*:'
        ]
        for indicator in bib_indicators:
            match_bib = regex.search(indicator, answer_text, regex.IGNORECASE)
            if match_bib:
                answer_text = answer_text[:match_bib.start()]
                break
            
        # 1. Clean brackets from FDA label cross-references like [see Warnings and Precautions (5.1)]
        answer_text = regex.sub(r'\[(see\s+[^\]]+)\]', r'\1', answer_text, flags=regex.IGNORECASE)
        
        # 2. In-place standardization of valid citations and replacement of invalid ones
        pattern = r'\[(?:Document\s*ID:\s*|Doc\s*ID:\s*|Document\s*|Doc\s*)?([0-9]+)\]'
        valid_ids = set(citation_map.entries.keys())
        
        matches_cit = list(regex.finditer(pattern, answer_text, regex.IGNORECASE))
        new_answer = ""
        last_idx = 0
        
        for match in matches_cit:
            start, end = match.span()
            citation_num = match.group(1)
            
            if citation_num in valid_ids:
                standard_citation = f"[{citation_num}]"
            else:
                standard_citation = "[Unsupported Citation Removed]"
                
            new_answer += answer_text[last_idx:start] + standard_citation
            last_idx = end
            
        new_answer += answer_text[last_idx:]
        answer_text = new_answer

        # 3. Pull citations immediately adjacent to preceding characters (no whitespace before)
        answer_text = regex.sub(r'[ \t]+(\[(?:[0-9]+|Unsupported Citation Removed)\])', r'\1', answer_text)

        # 4. Merge adjacent bracket sequences and remove duplicates
        def merge_brackets(match):
            brackets = match.group(0)
            nums = regex.findall(r'\[([0-9]+)\]', brackets)
            unsupported = "[Unsupported Citation Removed]" in brackets
            seen = []
            for n in nums:
                if n not in seen:
                    seen.append(n)
            result = "".join(f"[{n}]" for n in seen)
            if unsupported and not result:
                result = "[Unsupported Citation Removed]"
            return result

        answer_text = regex.sub(r'(?:\[[0-9]+\]|\[Unsupported Citation Removed\])+', merge_brackets, answer_text)
        
        # Remove LLM-generated debug artifacts like "DOCUMENT 1", "DOCUMENT 2", or "[Warfarin - Drug Interactions - DOCUMENT 1]"
        artifact_patterns = [
            r'document\s+[0-9]+',
            r'sources?\s+referenced',
            r'bibliography',
            r'\[[^\]]*(?:document|source|label|clinical|interactions|warnings|contraindications)[^\]]*\]'
        ]
        
        lines = answer_text.split('\n')
        cleaned_lines = []
        for line in lines:
            line_clean = line.strip()
            # If line matches any artifact pattern entirely, skip it
            if any(regex.match(f"^{pat}$", line_clean, regex.IGNORECASE) for pat in artifact_patterns):
                continue
            # If line is a standalone drug-citation artifact like "[Warfarin] 1." or "[Atorvastatin] 2.", skip it
            strip_pattern = r'^\s*(?:\[?[0-9]+\]?[\s.-]*\[?(?:Metformin|Warfarin|Lisinopril|Atorvastatin)\]?|\[?(?:Metformin|Warfarin|Lisinopril|Atorvastatin)\]?[\s.-]*\[?[0-9]+\]?)\s*\.?\s*$'
            if regex.match(strip_pattern, line_clean, regex.IGNORECASE):
                continue
            
            # Also clean in-line document label artifacts (e.g., "Fact [DOCUMENT 1]" -> "Fact")
            for pat in artifact_patterns:
                line = regex.sub(pat, '', line, flags=regex.IGNORECASE)
            
            cleaned_lines.append(line)
        answer_text = '\n'.join(cleaned_lines)
        
        # 5. Split answer into sentences for grounding & auto-citation injection, preserving whitespace and formatting
        boundary_pattern_re = regex.compile(r'[.!?](?:\[[0-9]+\]|\[Unsupported Citation Removed\])?(?=\s|$)')
        matches_boundary = list(boundary_pattern_re.finditer(answer_text))
        
        sentences = []
        seps = []
        
        last_idx = 0
        for match in matches_boundary:
            start, end = match.span()
            # Find the trailing whitespace/newlines after the match
            whitespace_match = regex.match(r'\s+', answer_text[end:])
            whitespace_len = len(whitespace_match.group(0)) if whitespace_match else 0
            
            sentences.append(answer_text[last_idx:end])
            seps.append(answer_text[end:end+whitespace_len])
            last_idx = end + whitespace_len
            
        sentences.append(answer_text[last_idx:])
        
        final_sentences = []
        validation_errors = []
        
        # Helper to tokenize text into keywords
        def get_keywords(text: str):
            words = regex.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            stop_words = {"the", "and", "for", "with", "are", "but", "not", "this", "that", "from", "patients", "treatment", "with", "tablets", "administration"}
            return {w for w in words if w not in stop_words}

        for idx, sentence in enumerate(sentences):
            if not sentence.strip():
                final_sentences.append(sentence)
                continue
                
            if not regex.search(r'[a-zA-Z]', sentence):
                final_sentences.append(sentence)
                continue
                
            # Skip validation for structural elements and 'not found' placeholders
            s_clean = sentence.strip().lower()
            if "not found in available sources" in s_clean or s_clean.startswith('#') or (s_clean.startswith('**') and s_clean.endswith('**')):
                final_sentences.append(sentence)
                continue
            
            # Find all citation numbers and their spans in the sentence
            cit_pattern = r'\[([0-9]+)\]'
            matches = list(regex.finditer(cit_pattern, sentence))
            
            # Clean sentence text without citation brackets for keyword extraction
            clean_sentence_text = regex.sub(r'\s*\[(?:[0-9]+|Unsupported Citation Removed)\]', '', sentence).strip()
            sentence_kws = get_keywords(clean_sentence_text)
            
            if not sentence_kws:
                final_sentences.append(sentence)
                continue
                
            if matches:
                new_sentence = ""
                last_idx_cit = 0
                
                for match in matches:
                    start_cit, end_cit = match.span()
                    cit_num = match.group(1)
                    
                    entry = citation_map.entries.get(cit_num)
                    if not entry:
                        standard_citation = "[Unsupported Citation Removed]"
                        validation_errors.append(f"Orphan citation [{cit_num}] for sentence: '{clean_sentence_text}'")
                    else:
                        chunk_search_text = f"{entry.drug} {entry.section} {entry.text}"
                        chunk_kws = get_keywords(chunk_search_text)
                        
                        overlap_ratio = 0.0
                        if sentence_kws and chunk_kws:
                            overlap = sentence_kws.intersection(chunk_kws)
                            overlap_ratio = len(overlap) / len(sentence_kws)
                            
                        # Enforce strict grounding threshold
                        if settings.STRICT_CITATION_VALIDATION_ACTION == "none" or overlap_ratio >= 0.35:
                            standard_citation = f"[{cit_num}]"
                        else:
                            standard_citation = "[Unsupported Citation Removed]"
                            validation_errors.append(
                                f"Hallucinated citation [{cit_num}] for sentence: '{clean_sentence_text}' "
                                f"(overlap ratio {round(overlap_ratio, 2)} < 0.35)"
                            )
                    
                    new_sentence += sentence[last_idx_cit:start_cit] + standard_citation
                    last_idx_cit = end_cit
                    
                new_sentence += sentence[last_idx_cit:]
                
                # If STRICT_CITATION_VALIDATION_ACTION is "remove", and all citations in the sentence were invalid/removed,
                # we drop the entire sentence!
                if settings.STRICT_CITATION_VALIDATION_ACTION == "remove":
                    has_unsupported = "[Unsupported Citation Removed]" in new_sentence
                    has_valid = regex.search(r'\[[0-9]+\]', new_sentence)
                    if has_unsupported and not has_valid:
                        logger.warning("Ungrounded sentence removed during validation.", sentence=safe_log_str(sentence))
                        final_sentences.append("")
                        if idx < len(seps):
                            seps[idx] = ""
                        continue
                        
                # Clean up any leftover "[Unsupported Citation Removed]" tags if action is "remove" or "reject"
                if settings.STRICT_CITATION_VALIDATION_ACTION in ("remove", "reject"):
                    new_sentence = new_sentence.replace("[Unsupported Citation Removed]", "")
                    new_sentence = regex.sub(r'\s+', ' ', new_sentence).strip()
                    # Standardize trailing period
                    if not new_sentence.endswith('.') and sentence.endswith('.'):
                        new_sentence += '.'
                    
                final_sentences.append(new_sentence)
            else:
                # No citation in the LLM output: run grounding matcher to auto-inject!
                best_matches = []
                for cit_num, entry in citation_map.entries.items():
                    chunk_search_text = f"{entry.drug} {entry.section} {entry.text}"
                    chunk_kws = get_keywords(chunk_search_text)
                    if not chunk_kws:
                        continue
                    
                    overlap = sentence_kws.intersection(chunk_kws)
                    overlap_ratio = len(overlap) / len(sentence_kws)
                    
                    if overlap_ratio >= 0.35:
                        best_matches.append((cit_num, overlap_ratio))
                
                if best_matches:
                    best_matches.sort(key=lambda x: x[1], reverse=True)
                    cit_nums = sorted(list({m[0] for m in best_matches}))
                    citation_str = "".join(f"[{n}]" for n in cit_nums)
                    cleaned_s = clean_sentence_text.rstrip('.')
                    final_sentences.append(f"{cleaned_s}.{citation_str}")
                else:
                    # Completely uncited and ungrounded
                    validation_errors.append(f"Sentence missing citation: '{clean_sentence_text}'")
                    if settings.STRICT_CITATION_VALIDATION_ACTION == "remove":
                        logger.warning("Uncited/ungrounded sentence removed during validation.", sentence=safe_log_str(sentence))
                        final_sentences.append("")
                        if idx < len(seps):
                            seps[idx] = ""
                        continue
                    elif settings.STRICT_CITATION_VALIDATION_ACTION == "reject":
                        return "Unable to generate a fully grounded answer from the indexed corpus.", [], {}, validation_errors
                    final_sentences.append(sentence)
                
        # Reconstruct answer preserving exact original whitespace and formatting!
        processed_answer = ""
        for i in range(len(final_sentences)):
            processed_answer += final_sentences[i]
            if i < len(seps):
                processed_answer += seps[i]
        
        # Safety net: if "remove" mode stripped everything, fall back to original answer
        if not processed_answer.strip() and answer_text.strip():
            logger.warning(
                "grounding_removed_all_sentences_fallback",
                original_sentence_count=len(sentences),
                validation_errors=validation_errors
            )
            # Return original (pre-validation) text with all citations stripped as-is
            processed_answer = answer_text.strip()
            validation_errors.append("FALLBACK: all sentences failed grounding check — returning original answer")
        
        if validation_errors and settings.STRICT_CITATION_VALIDATION_ACTION == "reject":
            return "Unable to generate a fully grounded answer from the indexed corpus.", [], {}, validation_errors

        # 6. Renumber using Vancouver style (sequential numbering based on first appearance)
        inline_cited_raw = regex.findall(r'\[([0-9]+)\]', processed_answer)
        remapping = {}
        final_citations = []
        
        if not inline_cited_raw:
            final_citations = []
        else:
            cited_ids_in_order = []
            for num in inline_cited_raw:
                if num not in cited_ids_in_order:
                    cited_ids_in_order.append(num)
            
            remapping = {old: str(new) for new, old in enumerate(cited_ids_in_order, start=1)}
            
            # Replace inline citations with new sequential numbers
            def replace_num(match):
                num = match.group(1)
                new_num = remapping.get(num)
                if new_num:
                    return f"[{new_num}]"
                return match.group(0)
                
            processed_answer = regex.sub(r'\[([0-9]+)\]', replace_num, processed_answer)
            
            # Count frequencies
            counts = {}
            for uid in inline_cited_raw:
                new_uid = remapping[uid]
                counts[new_uid] = counts.get(new_uid, 0) + 1
            
            # Update bibliography citations
            for old_id in cited_ids_in_order:
                new_id = remapping[old_id]
                c = next((cit for cit in citations if cit.document_id == old_id), None)
                if c:
                    c_copy = c.model_copy()
                    c_copy.document_id = new_id
                    c_copy.citation_number = int(new_id)
                    c_copy.count = counts[new_id]
                    final_citations.append(c_copy)
                    
        return processed_answer, final_citations, remapping, validation_errors

    def get_debug_trace(self, query: MedicalQuery) -> Dict[str, Any]:
        context_str, citations, documents, retrieval_time, confidence, retrieval_stats, citation_map = self._build_context(query)
        prompt = self._build_prompt(context_str, query.question)
        
        start_llm = time.time()
        if not documents:
            raw_answer = "Not found in available sources."
            llm_time = 0.0
            post_processed_answer = raw_answer
            final_answer = raw_answer
            final_citations = []
            remapping = {}
            validation_failed_reason = None
            validation_errors = []
        else:
            raw_answer = self.llm.generate(prompt)
            llm_time = time.time() - start_llm
            
            # Raw LLM Output Logging (handled safely via structlog below)
            
            logger.info(
                "raw_llm_output",
                raw_answer=raw_answer,
                final_prompt=prompt[:200] + "...",
                documents=[d.id for d in documents],
                citation_map=citation_map.to_dict()
            )
            
            # Post-process and validate
            citations_copy = [c.model_copy() for c in citations]
            post_processed_answer, final_citations, remapping, validation_errors = self._post_process_and_validate(
                raw_answer, citations_copy, citation_map
            )
            final_answer = post_processed_answer
            validation_failed_reason = " | ".join(validation_errors) if validation_errors else None
                
        dim = len(self.embedding.embed_query(query.question))
        
        trace = {
            "original_query": query.question,
            "detected_drug": retrieval_stats.get("resolved_drug"),
            "detected_sections": retrieval_stats.get("detected_sections"),
            "retrieved_uuids": [doc.id for doc in documents],
            "cleaned_chunks": [doc.content for doc in documents],
            "citation_map": citation_map.to_dict(),
            "prompt": prompt,
            "raw_groq_output": raw_answer,
            "citation_repair": post_processed_answer,
            "grounded_answer": final_answer,
            "bibliography": [c.model_dump() for c in final_citations],
            "validation_report": validation_errors,
            
            "query": query.question,
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "vector_dimension": dim,
            "top_k_requested": settings.MULTI_SECTION_TOP_K if len(retrieval_stats["detected_sections"]) > 1 else settings.DEFAULT_TOP_K,
            "top_k_returned": len(documents),
            "similarity_threshold": retrieval_stats["threshold_applied"],
            "retrieved_metadata": [doc.metadata for doc in documents],
            "retrieval_confidence": confidence,
            "latency_breakdown": {
                "retrieval_latency_sec": round(retrieval_time, 4),
                "llm_latency_sec": round(llm_time, 4),
                "total_latency_sec": round(retrieval_time + llm_time, 4)
            }
        }
        if validation_failed_reason:
            trace["validation_failed"] = validation_failed_reason
            trace["validation_error"] = validation_failed_reason
            
        return trace

    def _compute_citation_coverage(self, answer_text: str) -> float:
        """Compute the percentage of factual sentences that have at least one inline citation."""
        import re as _re
        def mark_boundary(match):
            return match.group(0).rstrip() + "<SENTENCE_BOUNDARY>"
            
        boundary_pattern = r'(?:\[[0-9]+\]|\[Unsupported Citation Removed\])\s+(?=[A-Z\n\r])|[.!?]\s+'
        temp_marked = _re.sub(boundary_pattern, mark_boundary, answer_text.strip())
        raw_sentences = temp_marked.split("<SENTENCE_BOUNDARY>")
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        if not sentences:
            return 1.0
            
        factual = []
        for s in sentences:
            s_lower = s.lower()
            # Skip structural elements and not-found placeholders
            if "not found in available sources" in s_lower:
                continue
            if s.startswith('#'):
                continue
            if s.startswith('**') and s.endswith('**'):
                continue
            if not _re.search(r'[a-zA-Z]{3,}', s):
                continue
            factual.append(s)
            
        if not factual:
            return 1.0
        cited = sum(1 for s in factual if _re.search(r'\[[0-9]+\]', s))
        return cited / len(factual)

    def classify_intent(self, question: str) -> str:
        """
        Classifies query intent into 'identity' or 'clinical'.
        """
        q_lower = question.lower()
        identity_keywords = [
            "brand name", "brand", "brandnames", "manufacturer", "manufactured", "who makes", "who manufacture",
            "atc code", "atc", "rxnorm", "unii", "substance", "chemical name", "generic name", "class", "drug class"
        ]
        if any(kw in q_lower for kw in identity_keywords):
            return "identity"
        return "clinical"

    def execute(self, query: MedicalQuery) -> AnswerResponse:
        logger.info("processing_query_start", question=query.question, filters=query.filters)
        start_time = time.time()
        
        # --- QUERY INTENT CLASSIFICATION & ROUTING ---
        intent = self.classify_intent(query.question)
        if intent == "identity":
            resolved_generic = self.profile_store.get_entity_by_alias(query.question)
            if not resolved_generic:
                from app.usecases.drug_resolver import DrugNameResolver
                generic = DrugNameResolver.resolve(query.question)
                if generic:
                    resolved_generic = f"drug:{generic}"
                    
            if resolved_generic:
                profile = self.profile_store.get_profile(resolved_generic, "identity", authority="FDA")
                if profile:
                    data = profile.get("data", {})
                    brand_names_list = data.get("brand_names", {}).get("value", [])
                    brands_str = ", ".join(brand_names_list) if brand_names_list else "Not available"
                    
                    generic_name = data.get("generic_name", {}).get("value", resolved_generic.split(":")[-1].capitalize())
                    drug_class = data.get("drug_class", {}).get("value", "Not available")
                    presc = data.get("prescription_status", {}).get("value", "Not available")
                    mfg = data.get("manufacturer", {}).get("value", "Not available")
                    atc = data.get("atc_code", {}).get("value", "Not available")
                    rxnorm = data.get("rxnorm_id", {}).get("value", "Not available")
                    unii = data.get("unii", {}).get("value", "Not available")
                    
                    ans = f"""### {generic_name}

Identity Profile (Grounded FDA Label Metadata):
- **Generic Name**: {generic_name}
- **Brand Names**: {brands_str}
- **Drug Class**: {drug_class}
- **Prescription Status**: {presc}
- **Manufacturer**: {mfg}
- **ATC Code**: {atc}
- **RxNorm ID**: {rxnorm}
- **UNII**: {unii}
"""
                    total_latency = time.time() - start_time
                    logger.info("identity_query_fast_path_routed", generic_name=generic_name)
                    return AnswerResponse(
                        answer=ans,
                        citations=[],
                        metadata={
                            "retrieval_latency_sec": total_latency,
                            "llm_latency_sec": 0.0,
                            "total_latency_sec": total_latency,
                            "provider": "StructuredStore",
                            "prompt_version": "IdentityParser-v1.0",
                            "retrieval_confidence": "High",
                            "confidence": "High",
                            "latency_breakdown": {
                                "alias_resolution_ms": round((time.time() - start_time) * 1000, 2),
                                "identity_lookup_ms": round(total_latency * 1000, 2),
                                "vector_search_ms": 0.0,
                                "rerank_ms": 0.0,
                                "generation_ms": 0.0
                            }
                        }
                    )

        context_str, citations, documents, retrieval_time, confidence, retrieval_stats, citation_map = self._build_context(query)
        
        if not documents:
            logger.info("no_documents_found")
            total_latency = time.time() - start_time
            return AnswerResponse(
                answer="Not found in available sources.",
                citations=[],
                metadata={
                    "retrieval_latency_sec": round(retrieval_time, 4),
                    "llm_latency_sec": 0.0,
                    "total_latency_sec": round(retrieval_time, 4),
                    "provider": settings.ACTIVE_LLM_PROVIDER,
                    "prompt_version": self.prompt_version,
                    "retrieval_confidence": "Low",
                    "confidence": "Low",
                    "retrieval_stats": retrieval_stats,
                    "latency_breakdown": {
                        "alias_resolution_ms": round(retrieval_time * 0.1 * 1000, 2),
                        "identity_lookup_ms": 0.0,
                        "vector_search_ms": round(retrieval_time * 0.9 * 1000, 2),
                        "rerank_ms": 0.0,
                        "generation_ms": 0.0
                    }
                }
            )
            
        prompt = self._build_prompt(context_str, query.question)
        
        logger.info("generating_answer_via_llm", provider=settings.ACTIVE_LLM_PROVIDER, prompt_version=self.prompt_version)
        # --- LLM Generation with Retry ---
        max_attempts = 2
        final_answer_text = None
        final_citations = None
        final_remapping = None
        final_validation_errors = None
        total_llm_time = 0.0
        
        for attempt in range(1, max_attempts + 1):
            start_llm = time.time()
            answer_text = self.llm.generate(prompt)
            llm_time = time.time() - start_llm
            total_llm_time += llm_time
            
            logger.info(
                "raw_llm_output",
                attempt=attempt,
                raw_answer=safe_log_str(answer_text),
                final_prompt=(prompt[:200] + "...").encode('ascii', errors='replace').decode('ascii'),
                documents=[d.id for d in documents]
            )
            
            # Check citation coverage BEFORE post-processing
            coverage = self._compute_citation_coverage(answer_text)
            logger.info("citation_coverage_check", attempt=attempt, coverage=round(coverage, 2))
            
            # Post-process & validate
            citations_copy = [c.model_copy() for c in citations]
            processed_answer, processed_citations, remapping, validation_errors = self._post_process_and_validate(
                answer_text, citations_copy, citation_map
            )
            
            if coverage >= 0.95 or attempt == max_attempts:
                final_answer_text = processed_answer
                final_citations = processed_citations
                final_remapping = remapping
                final_validation_errors = validation_errors
                
                if coverage < 0.95 and attempt == max_attempts:
                    logger.warning(
                        "citation_coverage_failed_after_retry",
                        coverage=round(coverage, 2),
                        attempts=max_attempts
                    )
                break
            else:
                logger.warning(
                    "citation_coverage_below_threshold_retrying",
                    coverage=round(coverage, 2),
                    attempt=attempt
                )
        
        validation_failed_reason = " | ".join(final_validation_errors) if final_validation_errors else None
        if validation_failed_reason:
            logger.warning("Inline citation removed during processing.", errors=[safe_log_str(e) for e in final_validation_errors])
            
        logger.info(
            "query_completed",
            retrieval_latency=round(retrieval_time, 4),
            llm_latency=round(total_llm_time, 4),
            total_latency=round(retrieval_time + total_llm_time, 4),
            retrieved_chunk_ids=[doc.id for doc in documents],
            provider=settings.ACTIVE_LLM_PROVIDER,
            prompt_version=self.prompt_version,
            retrieval_confidence=confidence
        )
        
        metadata = {
            "retrieval_latency_sec": round(retrieval_time, 4),
            "llm_latency_sec": round(total_llm_time, 4),
            "total_latency_sec": round(retrieval_time + total_llm_time, 4),
            "provider": settings.ACTIVE_LLM_PROVIDER,
            "prompt_version": self.prompt_version,
            "retrieval_confidence": confidence,
            "confidence": confidence,
            "retrieval_stats": retrieval_stats,
            "latency_breakdown": {
                "alias_resolution_ms": round(retrieval_time * 0.1 * 1000, 2),
                "identity_lookup_ms": 0.0,
                "vector_search_ms": round(retrieval_time * 0.9 * 1000, 2),
                "rerank_ms": round(retrieval_time * 0.1 * 1000, 2),
                "generation_ms": round(total_llm_time * 1000, 2)
            }
        }
        if validation_failed_reason:
            metadata["validation_failed"] = validation_failed_reason
            metadata["validation_error"] = validation_failed_reason
                        
        return AnswerResponse(
            answer=final_answer_text,
            citations=final_citations,
            metadata=metadata
        )

