from typing import List, Tuple, Any, Dict
import time
import re
from app.domain.models import MedicalQuery, AnswerResponse, Citation, ReferenceDocument
from app.domain.interfaces import LLMProviderProtocol, VectorDatabaseProtocol, EmbeddingModelProtocol, CrossEncoderProtocol
from app.usecases.query_expansion import LayeredQueryExpander
from app.core.config import settings
import structlog

logger = structlog.get_logger()

SECTION_KEYWORDS = {
    "Contraindications": ["contraindication", "contraindicated"],
    "Warnings": ["warning", "precaution", "boxed warning", "black box", "warnings"],
    "Precautions": ["precaution", "warning", "precautions"],
    "Pregnancy": ["pregnancy", "pregnant", "teratogenic", "fetus"],
    "Lactation": ["lactation", "nursing", "breast milk", "human milk"],
    "Pediatric Use": ["pediatric", "child", "children"],
    "Geriatric Use": ["geriatric", "elderly", "older patients"],
    "Adverse Reactions": ["adverse", "side effect", "clinical trials", "experience", "postmarketing", "reactions"],
    "Overdosage": ["overdosage", "overdose"],
    "Storage": ["storage", "handling", "supplied", "store", "keep"],
    "Drug Interactions": ["interaction", "interactions", "concomitant"],
    "Dosage": ["dosage", "administration", "dosing"]
}

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
        self.expander = LayeredQueryExpander(llm_provider)
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
        section_keyword_map = {
            "contraindication": "Contraindications",
            "warning": "Warnings",
            "boxed warning": "Warnings",
            "black box": "Warnings",
            "precaution": "Precautions",
            "pregnancy": "Pregnancy",
            "lactation": "Lactation",
            "nursing": "Lactation",
            "pediatric": "Pediatric Use",
            "child": "Pediatric Use",
            "geriatric": "Geriatric Use",
            "elderly": "Geriatric Use",
            "adverse": "Adverse Reactions",
            "side effect": "Adverse Reactions",
            "overdosage": "Overdosage",
            "storage": "Storage",
            "interaction": "Drug Interactions",
            "counseling": "Patient Counseling Information",
            "dosage": "Dosage",
            "administration": "Dosage",
            "indication": "Indications"
        }
        
        q_lower = query.question.lower()
        detected_sections = []
        for kw, canonical_sec in section_keyword_map.items():
            if kw in q_lower:
                detected_sections.append(canonical_sec)
        detected_sections = list(set(detected_sections))
        
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
                
                # Sort and prioritize for this drug
                drug_docs = list(drug_retrieved.values())
                drug_docs.sort(key=lambda x: x.score or 0.0, reverse=True)
                
                if detected_sections:
                    in_section = []
                    for d in drug_docs:
                        db_sec = d.metadata.get("section", "").lower()
                        matched = False
                        for ds in detected_sections:
                            kws = SECTION_KEYWORDS.get(ds, [ds.lower()])
                            for kw in kws:
                                if kw in db_sec:
                                    matched = True
                                    break
                            if matched:
                                break
                        if matched:
                            in_section.append(d)
                    
                    # STRICT METADATA FILTERING: Drop out_section chunks entirely
                    drug_docs = in_section
                
                threshold = settings.SIMILARITY_THRESHOLD
                drug_threshold_docs = [d for d in drug_docs if (d.score or 0.0) >= threshold]
                if not drug_threshold_docs and drug_docs:
                    drug_threshold_docs = [d for d in drug_docs if (d.score or 0.0) >= 0.35]
                
                total_filtered += len(drug_threshold_docs)
                # Keep top 3 for this drug to guarantee balance
                all_retrieved_docs_by_drug.extend(drug_threshold_docs[:3])
            
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
                
            if detected_sections:
                in_section = []
                for d in filtered_docs:
                    db_sec = d.metadata.get("section", "").lower()
                    matched = False
                    for ds in detected_sections:
                        kws = SECTION_KEYWORDS.get(ds, [ds.lower()])
                        for kw in kws:
                            if kw in db_sec:
                                matched = True
                                break
                        if matched:
                            break
                    if matched:
                        in_section.append(d)
                
                # STRICT METADATA FILTERING: Drop out_section chunks entirely
                filtered_docs = in_section
                
            threshold = settings.SIMILARITY_THRESHOLD
            threshold_filtered_docs = [d for d in filtered_docs if (d.score or 0.0) >= threshold]
            if not threshold_filtered_docs and filtered_docs:
                threshold_filtered_docs = [d for d in filtered_docs if (d.score or 0.0) >= 0.35]
                
            total_filtered += len(threshold_filtered_docs)
            final_docs = threshold_filtered_docs[:settings.MAX_CONTEXT_CHUNKS]
            
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
        context_str = ""
        citations = []
        for i, doc in enumerate(final_docs, start=1):
            citation_id = str(i)
            # Sequential citations
            context_str += f"[Document ID: {citation_id}]\nSource: {doc.source} - {doc.metadata.get('drug_name', doc.metadata.get('drug', ''))} - {doc.metadata.get('section', '')}\nContent: {doc.content}\n\n"
            citations.append(Citation(
                document_id=citation_id,
                source=f"{doc.source} – {doc.metadata.get('drug_name', doc.metadata.get('drug', ''))} – {doc.metadata.get('section', '')}",
                snippet=doc.content,
                uuid=doc.id,
                drug=doc.metadata.get('drug_name', doc.metadata.get('drug', '')),
                section=doc.metadata.get('section', ''),
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
            "detected_sections": detected_sections
        }
        
        return context_str, citations, final_docs, retrieve_time, confidence, retrieval_stats

    def _build_prompt(self, context_str: str, question: str) -> str:
        return f"""
Context:
{context_str}

Question: {question}

Instructions:
1. Answer the question using ONLY the provided context.
2. Cite every fact with its corresponding [X] where X is the sequential Document ID number of the document (e.g. [1], [2]).
3. EVERY factual sentence MUST end with at least one citation.
4. Place citations IMMEDIATELY after every factual statement or sentence. For example: "Metformin decreases hepatic glucose production.[1]"
5. CRITICAL: Never place citations on a separate line or separate paragraph. For example, do NOT do this:
Metformin decreases hepatic glucose production.
[1]
All citations must be inline and directly attached to the statement they support.
6. If the requested information is not explicitly present in the retrieved context, return exactly: "Not found in available sources."
7. Do NOT provide any additional explanation, notes, disclaimers, or adjacent/related clinical information if the information is not found. Do NOT say things like "However, the context mentions..." or "Note: ...". Just return exactly "Not found in available sources." and nothing else.
8. Do not generalize or extrapolate beyond the provided text.
        """

    def get_debug_retrieval(self, query: MedicalQuery):
        _, _, documents, total_retrieval_time, confidence, retrieval_stats = self._build_context(query)
        return {
            "retrieval_time_sec": round(total_retrieval_time, 4),
            "retrieved_chunks": [
                {
                    "uuid": doc.id,
                    "score": doc.score,
                    "content": doc.content,
                    "drug": doc.metadata.get("drug_name", doc.metadata.get("drug", "")),
                    "section": doc.metadata.get("section", ""),
                    "source": doc.source,
                    "chunk_length": len(doc.content),
                    "embedding_dimension": len(self.embedding.embed_query(query.question)),
                    "document_version": doc.metadata.get("version", "1.0.0"),
                    "rank": i + 1
                }
                for i, doc in enumerate(documents)
            ],
            "metrics": {
                "retrieval_latency_sec": retrieval_stats["retrieval_latency_sec"],
                "total_retrieved": retrieval_stats["total_retrieved"],
                "total_filtered": retrieval_stats["total_filtered"],
                "threshold_applied": retrieval_stats["threshold_applied"],
                "confidence": confidence
            }
        }
        
    def get_debug_prompt(self, query: MedicalQuery):
        context_str, _, _, _, _, _ = self._build_context(query)
        prompt = self._build_prompt(context_str, query.question)
        return {
            "prompt_version": self.prompt_version,
            "provider": settings.ACTIVE_LLM_PROVIDER,
            "generated_prompt": prompt
        }

    def get_debug_trace(self, query: MedicalQuery) -> Dict[str, Any]:
        context_str, citations, documents, retrieval_time, confidence, retrieval_stats = self._build_context(query)
        prompt = self._build_prompt(context_str, query.question)
        
        start_llm = time.time()
        if not documents:
            answer_text = "Not found in available sources."
            llm_time = 0.0
        else:
            answer_text = self.llm.generate(prompt)
            llm_time = time.time() - start_llm
            
        dim = len(self.embedding.embed_query(query.question))
        
        return {
            "query": query.question,
            "embedding_model": settings.EMBEDDING_MODEL_NAME,
            "vector_dimension": dim,
            "top_k_requested": settings.MULTI_SECTION_TOP_K if len(retrieval_stats["detected_sections"]) > 1 else settings.DEFAULT_TOP_K,
            "top_k_returned": len(documents),
            "similarity_threshold": retrieval_stats["threshold_applied"],
            "retrieved_uuids": [doc.id for doc in documents],
            "retrieved_metadata": [doc.metadata for doc in documents],
            "prompt_sent": prompt,
            "answer": answer_text,
            "bibliography": [c.model_dump() for c in citations],
            "retrieval_confidence": confidence,
            "latency_breakdown": {
                "retrieval_latency_sec": round(retrieval_time, 4),
                "llm_latency_sec": round(llm_time, 4),
                "total_latency_sec": round(retrieval_time + llm_time, 4)
            }
        }

    def execute(self, query: MedicalQuery) -> AnswerResponse:
        logger.info("processing_query_start", question=query.question, filters=query.filters)
        
        context_str, citations, documents, retrieval_time, confidence, retrieval_stats = self._build_context(query)
        
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
        start_llm = time.time()
        answer_text = self.llm.generate(prompt)
        llm_time = time.time() - start_llm
        
        # Post-processing citation validation (Tied to Chunks)
        if "Not found in available sources" in answer_text:
            answer_text = "Not found in available sources."
            citations = []
        else:
            # We match variations like [1], [Document 1], [Doc 1], [Document ID: 1], etc.
            pattern = r'\[(?:Document\s*ID:\s*|Doc\s*ID:\s*|Document\s*|Doc\s*)?([0-9]+)\]'
            
            valid_ids = {c.document_id for c in citations}
            
            # Find and standardize or remove citations
            matches = list(re.finditer(pattern, answer_text, re.IGNORECASE))
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

            # 1. Pull citations immediately adjacent to preceding characters (no whitespace before)
            answer_text = re.sub(r'\s+(\[(?:[0-9]+|Unsupported Citation Removed)\])', r'\1', answer_text)

            # 2. Merge adjacent bracket sequences and remove duplicates
            def merge_brackets(match):
                brackets = match.group(0)
                nums = re.findall(r'\[([0-9]+)\]', brackets)
                unsupported = "[Unsupported Citation Removed]" in brackets
                seen = []
                for n in nums:
                    if n not in seen:
                        seen.append(n)
                result = "".join(f"[{n}]" for n in seen)
                if unsupported and not result:
                    result = "[Unsupported Citation Removed]"
                return result

            answer_text = re.sub(r'(?:\[[0-9]+\]|\[Unsupported Citation Removed\])+', merge_brackets, answer_text)

            # 3. Handle fallback or filter/count bibliography entries
            inline_cited_raw = re.findall(r'\[([0-9]+)\]', answer_text)
            if not inline_cited_raw and citations:
                # If no citations were parsed, append [1] as fallback directly adjacent
                answer_text = answer_text.strip()
                if not answer_text.endswith("]"):
                    answer_text += "[1]"
                citations = [citations[0]]
                citations[0].count = 1
            else:
                # Vancouver renumbering based on first appearance order
                cited_ids_in_order = []
                for num in inline_cited_raw:
                    if num not in cited_ids_in_order:
                        cited_ids_in_order.append(num)
                
                remapping = {old: str(new) for new, old in enumerate(cited_ids_in_order, start=1)}
                
                # Replace the brackets in the text with the new numbers
                def replace_num(match):
                    num = match.group(1)
                    new_num = remapping.get(num)
                    if new_num:
                        return f"[{new_num}]"
                    return match.group(0)
                    
                answer_text = re.sub(r'\[([0-9]+)\]', replace_num, answer_text)
                
                # Count frequencies of new sequential numbers in post-processed text
                counts = {}
                for uid in inline_cited_raw:
                    new_uid = remapping[uid]
                    counts[new_uid] = counts.get(new_uid, 0) + 1
                
                # Sort and update bibliography list based on the new sequential mapping
                final_citations = []
                for old_id in cited_ids_in_order:
                    new_id = remapping[old_id]
                    c = next((cit for cit in citations if cit.document_id == old_id), None)
                    if c:
                        c.document_id = new_id
                        c.count = counts[new_id]
                        final_citations.append(c)
                citations = final_citations
            
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
        # Phase 1.7.2 Citation Validation
        if "not found in available sources" not in answer_text.lower():
            # Check if there are no citations at all
            if not citations:
                answer_text = "Unable to generate a fully grounded answer from the indexed corpus."
                logger.error("validation_failed", reason="no_citations")
                citations = []
            else:
                # Check for uncited factual sentences
                import re as regex
                sentences = [s.strip() for s in regex.split(r'(?<=\.)\s+', answer_text) if s.strip()]
                for sentence in sentences:
                    if sentence and not regex.search(r'\[([0-9]+)\]', sentence):
                        logger.error("validation_failed", reason="uncited_sentence", sentence=sentence)
                        answer_text = "Unable to generate a fully grounded answer from the indexed corpus."
                        citations = []
                        break
                        
        return AnswerResponse(
            answer=answer_text,
            citations=citations,
            metadata={
                "retrieval_latency_sec": round(retrieval_time, 4),
                "llm_latency_sec": round(llm_time, 4),
                "total_latency_sec": round(retrieval_time + llm_time, 4),
                "provider": settings.ACTIVE_LLM_PROVIDER,
                "prompt_version": self.prompt_version,
                "retrieval_confidence": confidence,
                "retrieval_stats": retrieval_stats
            }
        )

