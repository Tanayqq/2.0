from typing import List, Tuple, Any, Dict
import time
import re
from app.domain.models import MedicalQuery, AnswerResponse, Citation, ReferenceDocument
from app.domain.interfaces import LLMProviderProtocol, VectorDatabaseProtocol, EmbeddingModelProtocol, CrossEncoderProtocol
from app.usecases.query_expansion import LayeredQueryExpander
from app.citation_map import CitationMap
from app.core.config import settings
from app.section_utils import normalize_section
import structlog

logger = structlog.get_logger()

SECTION_KEYWORDS = {
    "contraindications": ["contraindication", "contraindications", "contraindicated"],
    "warnings": ["warning", "warnings", "boxed warning", "boxed warnings", "black box", "blackbox"],
    "precautions": ["precaution", "precautions"],
    "pregnancy": ["pregnancy", "pregnant", "teratogenic", "fetus", "fetal"],
    "lactation": ["lactation", "nursing", "breast milk", "breastfeeding", "human milk"],
    "pediatric use": ["pediatric", "pediatrics", "child", "children", "infant", "infants", "adolescent", "adolescents"],
    "geriatric use": ["geriatric", "geriatrics", "elderly", "older patients", "aging"],
    "adverse reactions": ["adverse", "adverse reaction", "adverse reactions", "side effect", "side effects"],
    "overdosage": ["overdosage", "overdose", "overdoses"],
    "storage": ["storage", "handling", "supplied", "store", "keep"],
    "drug interactions": ["interaction", "interactions", "drug interaction", "drug interactions", "concomitant"],
    "dosage": ["dosage", "dosages", "administration", "dosing", "dose", "doses"],
    # Note: 'use'/'uses' intentionally excluded — too broad, fires on nearly every query
    "indications": ["indication", "indications", "indicated"],
    "patient counseling information": ["counseling", "patient counseling"]
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

    def _build_context(self, query: MedicalQuery) -> Tuple[str, List[Citation], List[Any], float, str, Dict[str, Any]]:
        start_retrieve = time.time()
        
        # 1. Resolve drug name using DrugNameResolver
        from app.usecases.drug_resolver import DrugNameResolver
        
        # Detect all drugs in the question to support multi-drug comparisons
        detected_drugs = []
        words = [w.strip("?,.:;!\"'()[]{}").lower() for w in query.question.split()]
        for word in words:
            if word in DrugNameResolver.GENERIC_NAMES:
                detected_drugs.append(word)
            elif word in DrugNameResolver.BRAND_TO_GENERIC:
                detected_drugs.append(DrugNameResolver.BRAND_TO_GENERIC[word])
                
        # Multi-word/substring check for generic/brand matching
        query_lower = query.question.lower()
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
        
        # 2. Detect requested clinical sections
        q_lower = query.question.lower()
        detected_sections = []
        import re
        for canonical_sec, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                    detected_sections.append(canonical_sec)
                    break
        detected_sections = list(set(detected_sections))
        
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
        has_sections = len(detected_sections) > 0
        top_k_to_request = settings.MULTI_SECTION_TOP_K if has_sections else settings.DEFAULT_TOP_K
        
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
                    
                    db_filters = dict(query.filters) if query.filters else {}
                    db_filters["drug"] = drug
                    
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
                diversified_drug_docs = _balance_by_section(drug_threshold_docs, detected_sections, max_total=3)
                all_retrieved_docs_by_drug.extend(diversified_drug_docs)
            
            final_docs = all_retrieved_docs_by_drug
        else:
            # Single drug or no resolved drug
            all_retrieved_docs: dict[str, ReferenceDocument] = {}
            for q in expanded_queries:
                dense_vec = self.embedding.embed_query(q)
                sparse_vec = self.embedding.embed_sparse(q)
                
                db_filters = dict(query.filters) if query.filters else {}
                if resolved_drug:
                    db_filters["drug"] = resolved_drug
                
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
            # Diversify by section to ensure all requested sections are represented!
            final_docs = _balance_by_section(threshold_filtered_docs, detected_sections, max_total=settings.MAX_CONTEXT_CHUNKS)
            
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

        # 7. Assign sequential internal citation IDs
        citation_map = CitationMap()
        context_str = ""
        citations = []
        for i, doc in enumerate(final_docs, start=1):
            citation_id = str(i)
            drug = doc.metadata.get('drug_name', doc.metadata.get('drug', ''))
            section = doc.metadata.get('section', doc.metadata.get('category', ''))
            
            # Normalize chunk content using preprocessor
            from app.preprocessor import clean_chunk_content
            cleaned_content = clean_chunk_content(doc.content)
            
            # Format document representation exactly as requested
            context_str += f"=========================\n\n"
            context_str += f"DOCUMENT {citation_id}\n\n"
            context_str += f"Citation Number: [{citation_id}]\n\n"
            context_str += f"UUID:\n{doc.id}\n\n"
            context_str += f"Drug:\n{drug}\n\n"
            context_str += f"Section:\n{section}\n\n"
            context_str += f"Source:\n{doc.source}\n\n"
            context_str += f"Facts\n"
            for line in cleaned_content.split('\n'):
                if line.strip():
                    context_str += f"{line}\n"
            context_str += f"\n=========================\n\n"
            
            # Add to citation map (using cleaned content)
            citation_map.add_entry(
                uuid=doc.id,
                citation_number=citation_id,
                source=doc.source,
                drug=drug,
                section=section,
                text=cleaned_content,
                similarity=round(doc.score or 0.0, 4)
            )
            
            # Add to citations (legacy list for bibliography)
            citations.append(Citation(
                document_id=citation_id,
                source=f"{doc.source} – {drug} – {section}",
                snippet=cleaned_content,
                uuid=doc.id,
                drug=drug,
                section=section,
                similarity=round(doc.score or 0.0, 4),
                count=0
            ))
            
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
            "rejection_log": rejection_log
        }
        
        return context_str, citations, final_docs, retrieve_time, confidence, retrieval_stats, citation_map

    def _build_prompt(self, context_str: str, question: str) -> str:
        return f"""
Context:
{context_str}

Question: {question}

Instructions:
You are a clinical summarization engine.
You are NOT allowed to answer from memory.
You may ONLY summarize the numbered DOCUMENTS.
Each DOCUMENT already has its citation number.
After EVERY factual sentence append its citation.

Example:
Metformin is contraindicated in severe renal impairment.[1]
Metformin is contraindicated in hypersensitivity.[1]

Never output "[see Warnings]" or FDA label references.
Never invent citation numbers.
Never omit citations.
Never merge facts from different drugs.

You are provided with retrieved chunks that belong to specific clinical sections. If the user requests only one section (for example "Contraindications"), you must answer exclusively from chunks whose metadata section equals that requested section. Ignore all other retrieved sections. Do not include warnings, precautions, patient package inserts, adverse reactions, or indications unless they were explicitly requested.

If no chunk exists for the requested section, or if the information does not exist in the context, respond exactly:
Not found in available sources.
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
        
        # Section detection (same logic)
        import re as _re
        detected_sections_debug = []
        for canonical_sec, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if _re.search(r'\b' + _re.escape(kw) + r'\b', q_lower):
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
            
        # 1. Clean brackets from FDA label cross-references like [see Warnings and Precautions (5.1)]
        answer_text = regex.sub(r'\[(see\s+[^\]]+)\]', r'\1', answer_text, flags=regex.IGNORECASE)
        
        # 2. In-place standardization of valid citations and replacement of invalid ones
        pattern = r'\[(?:Document\s*ID:\s*|Doc\s*ID:\s*|Document\s*|Doc\s*)?([0-9]+)\]'
        valid_ids = set(citation_map.entries.keys())
        
        matches = list(regex.finditer(pattern, answer_text, regex.IGNORECASE))
        new_answer = ""
        last_idx = 0
        
        for match in matches:
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
        answer_text = regex.sub(r'\s+(\[(?:[0-9]+|Unsupported Citation Removed)\])', r'\1', answer_text)

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
        
        # 5. Split answer into sentences for grounding & auto-citation injection
        def mark_boundary(match):
            return match.group(0).rstrip() + "<SENTENCE_BOUNDARY>"
            
        boundary_pattern = r'(?:\[[0-9]+\]|\[Unsupported Citation Removed\])\s+(?=[A-Z\n\r])|[.!?]\s+'
        temp_marked = regex.sub(boundary_pattern, mark_boundary, answer_text.strip())
        raw_sentences = temp_marked.split("<SENTENCE_BOUNDARY>")
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        final_sentences = []
        validation_errors = []
        
        # Helper to tokenize text into keywords
        def get_keywords(text: str):
            words = regex.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            stop_words = {"the", "and", "for", "with", "are", "but", "not", "this", "that", "from", "patients", "treatment", "with", "tablets", "administration"}
            return {w for w in words if w not in stop_words}

        for sentence in sentences:
            if not regex.search(r'[a-zA-Z]', sentence):
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
                last_idx = 0
                
                for match in matches:
                    start, end = match.span()
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
                    
                    new_sentence += sentence[last_idx:start] + standard_citation
                    last_idx = end
                    
                new_sentence += sentence[last_idx:]
                
                # If STRICT_CITATION_VALIDATION_ACTION is "remove", and all citations in the sentence were invalid/removed,
                # we drop the entire sentence!
                if settings.STRICT_CITATION_VALIDATION_ACTION == "remove":
                    has_unsupported = "[Unsupported Citation Removed]" in new_sentence
                    has_valid = regex.search(r'\[[0-9]+\]', new_sentence)
                    if has_unsupported and not has_valid:
                        logger.warning("Ungrounded sentence removed during validation.", sentence=sentence)
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
                        logger.warning("Uncited/ungrounded sentence removed during validation.", sentence=sentence)
                        continue
                    elif settings.STRICT_CITATION_VALIDATION_ACTION == "reject":
                        return "Unable to generate a fully grounded answer from the indexed corpus.", [], {}, validation_errors
                    final_sentences.append(sentence)
                
        # Reconstruct answer
        processed_answer = " ".join(final_sentences)
        
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
            logger.info("complete_prompt", prompt=prompt)
            raw_answer = self.llm.generate(prompt)
            llm_time = time.time() - start_llm
            
            # Raw LLM Output Logging (handled safely via structlog below)
            
            logger.info(
                "raw_llm_output",
                raw_answer=raw_answer,
                final_prompt=prompt,
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

    def execute(self, query: MedicalQuery) -> AnswerResponse:
        logger.info("processing_query_start", question=query.question, filters=query.filters)
        
        context_str, citations, documents, retrieval_time, confidence, retrieval_stats, citation_map = self._build_context(query)
        
        if not documents:
            logger.info("no_documents_found")
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
                    "retrieval_stats": retrieval_stats
                }
            )
            
        prompt = self._build_prompt(context_str, query.question)
        
        logger.info("generating_answer_via_llm", provider=settings.ACTIVE_LLM_PROVIDER, prompt_version=self.prompt_version)
        logger.info("complete_prompt", prompt=prompt)
        
        start_llm = time.time()
        answer_text = self.llm.generate(prompt)
        llm_time = time.time() - start_llm
        
        # B. Raw LLM Output Logging (handled safely via structlog below)
        
        logger.info(
            "raw_llm_output",
            raw_answer=answer_text,
            final_prompt=prompt,
            documents=[d.id for d in documents],
            citation_map=citation_map.to_dict()
        )
        
        # Post-process & validate
        answer_text, citations, remapping, validation_errors = self._post_process_and_validate(
            answer_text, citations, citation_map
        )
        
        validation_failed_reason = " | ".join(validation_errors) if validation_errors else None
        if validation_failed_reason:
            logger.warning("Inline citation removed during processing.", errors=validation_errors)
            
        logger.info(
            "query_completed",
            retrieval_latency=round(retrieval_time, 4),
            llm_latency=round(llm_time, 4),
            total_latency=round(retrieval_time + llm_time, 4),
            retrieved_chunk_ids=[doc.id for doc in documents],
            provider=settings.ACTIVE_LLM_PROVIDER,
            prompt_version=self.prompt_version,
            retrieval_confidence=confidence
        )
        
        metadata = {
            "retrieval_latency_sec": round(retrieval_time, 4),
            "llm_latency_sec": round(llm_time, 4),
            "total_latency_sec": round(retrieval_time + llm_time, 4),
            "provider": settings.ACTIVE_LLM_PROVIDER,
            "prompt_version": self.prompt_version,
            "retrieval_confidence": confidence,
            "retrieval_stats": retrieval_stats
        }
        if validation_failed_reason:
            metadata["validation_failed"] = validation_failed_reason
            metadata["validation_error"] = validation_failed_reason
                        
        return AnswerResponse(
            answer=answer_text,
            citations=citations,
            metadata=metadata
        )

