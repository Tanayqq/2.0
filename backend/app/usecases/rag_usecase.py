from typing import List, Tuple, Any
import time
import re
from app.domain.models import MedicalQuery, AnswerResponse, Citation, ReferenceDocument
from app.domain.interfaces import LLMProviderProtocol, VectorDatabaseProtocol, EmbeddingModelProtocol, CrossEncoderProtocol
from app.usecases.query_expansion import LayeredQueryExpander
from app.core.config import settings
import structlog

logger = structlog.get_logger()

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
        
        # We retrieve more initially for re-ranking
        self.initial_top_k = 20
        self.final_top_k = 5

    def _build_context(self, query: MedicalQuery) -> Tuple[str, List[Citation], List[Any], float]:
        start_retrieve = time.time()
        
        # 1. Query Expansion (Ontology -> LLM)
        expanded_queries = self.expander.expand(query.question)
        
        all_retrieved_docs: dict[str, ReferenceDocument] = {}
        
        # 2. Search for all query variations
        for q in expanded_queries:
            dense_vec = self.embedding.embed_query(q)
            sparse_vec = self.embedding.embed_sparse(q)
            
            if sparse_vec:
                # Hybrid Search (Dense + Sparse) when SPLADE is available
                docs = self.vector_db.hybrid_search(
                    dense_vector=dense_vec,
                    sparse_vector=sparse_vec,
                    top_k=self.initial_top_k,
                    filters=query.filters
                )
            else:
                # Dense-only search (free tier mode)
                docs = self.vector_db.search(
                    query_vector=dense_vec,
                    top_k=self.initial_top_k,
                    filters=query.filters
                )
            
            # Deduplicate by Document ID
            for doc in docs:
                all_retrieved_docs[doc.id] = doc
                
        merged_docs = list(all_retrieved_docs.values())
        
        # 3. Cross-Encoder Re-ranking
        # Re-score all unique retrieved documents against the original user query
        reranked_docs = self.cross_encoder.rerank(query.question, merged_docs, top_k=self.final_top_k)
        
        retrieve_time = time.time() - start_retrieve
        
        context_str = ""
        citations = []
        for i, doc in enumerate(reranked_docs, start=1):
            citation_id = str(i)
            context_str += f"[Document ID: {citation_id}]\nSource: {doc.source}\nContent: {doc.content}\n\n"
            citations.append(Citation(
                document_id=citation_id,
                source=doc.source,
                snippet=doc.content[:150] + "..."
            ))
            
        return context_str, citations, reranked_docs, retrieve_time

    def _build_prompt(self, context_str: str, question: str) -> str:
        return f"""
Context:
{context_str}

Question: {question}

Instructions:
1. Answer the question using ONLY the provided context.
2. Cite every fact with its corresponding [Document ID: X] where X is the number of the document.
3. If the requested information is not explicitly present in the retrieved context, return exactly: "Not found in available sources."
4. Do NOT provide any additional explanation, notes, disclaimers, or adjacent/related clinical information if the information is not found. Do NOT say things like "However, the context mentions..." or "Note: ...". Just return exactly "Not found in available sources." and nothing else.
5. Do not generalize or extrapolate beyond the provided text.
        """

    def get_debug_retrieval(self, query: MedicalQuery):
        _, _, documents, total_retrieval_time = self._build_context(query)
        return {
            "retrieval_time_sec": round(total_retrieval_time, 4),
            "retrieved_chunks": [doc.model_dump() for doc in documents]
        }
        
    def get_debug_prompt(self, query: MedicalQuery):
        context_str, _, _, _ = self._build_context(query)
        prompt = self._build_prompt(context_str, query.question)
        return {
            "prompt_version": self.prompt_version,
            "provider": settings.ACTIVE_LLM_PROVIDER,
            "generated_prompt": prompt
        }

    def execute(self, query: MedicalQuery) -> AnswerResponse:
        logger.info("processing_query_start", question=query.question, filters=query.filters)
        
        context_str, citations, documents, retrieval_time = self._build_context(query)
        
        if not documents:
            logger.info("no_documents_found")
            return AnswerResponse(
                answer="Not found in available sources.",
                citations=[]
            )
            
        prompt = self._build_prompt(context_str, query.question)
        
        logger.info("generating_answer_via_llm", provider=settings.ACTIVE_LLM_PROVIDER, prompt_version=self.prompt_version)
        start_llm = time.time()
        answer_text = self.llm.generate(prompt)
        llm_time = time.time() - start_llm
        
        # Post-processing citation validation
        if "Not found in available sources" in answer_text:
            answer_text = "Not found in available sources."
            citations = []
        else:
            cited_ids = re.findall(r'\[Document ID:\s*([^\]]+)\]', answer_text)
            valid_ids = {c.document_id for c in citations}
            
            citations = [c for c in citations if c.document_id in cited_ids and c.document_id in valid_ids]
            
            hallucinated_ids = set(cited_ids) - valid_ids
            for hallucinated_id in hallucinated_ids:
                answer_text = re.sub(rf'\[Document ID:\s*{re.escape(hallucinated_id)}\]', '', answer_text)
            
        logger.info(
            "query_completed",
            retrieval_latency=round(retrieval_time, 4),
            llm_latency=round(llm_time, 4),
            total_latency=round(retrieval_time + llm_time, 4),
            retrieved_chunk_ids=[doc.id for doc in documents],
            provider=settings.ACTIVE_LLM_PROVIDER,
            prompt_version=self.prompt_version
        )
            
        return AnswerResponse(
            answer=answer_text,
            citations=citations,
            metadata={
                "retrieval_latency_sec": round(retrieval_time, 4),
                "llm_latency_sec": round(llm_time, 4),
                "total_latency_sec": round(retrieval_time + llm_time, 4),
                "provider": settings.ACTIVE_LLM_PROVIDER,
                "prompt_version": self.prompt_version
            }
        )
