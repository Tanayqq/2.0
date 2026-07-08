from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Dict
from app.domain.interfaces import EmbeddingModelProtocol, CrossEncoderProtocol
from fastembed import SparseTextEmbedding
from sentence_transformers import CrossEncoder

class MedCPTEmbeddingModel(EmbeddingModelProtocol):
    """
    Local implementation of MedCPT for dense medical embeddings, combined with
    SPLADE via fastembed for sparse keyword extraction (Hybrid Search).
    """
    def __init__(self, model_name: str = "ncbi/MedCPT-Query-Encoder"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
        # Initialize Sparse Embedder for Hybrid Search (BM25/SPLADE)
        self.sparse_model = SparseTextEmbedding(model_name="prithvida/Splade_PP_en_v1")

    def embed_query(self, text: str) -> List[float]:
        # Dense Embedding
        inputs = self.tokenizer(text, truncation=True, padding=True, return_tensors='pt', max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings.cpu().numpy()[0].tolist()

    def embed_sparse(self, text: str) -> Dict[int, float]:
        # Sparse Embedding (SPLADE)
        sparse_result = list(self.sparse_model.embed([text]))[0]
        # fastembed returns indices and values. We map them to a dict.
        return {int(idx): float(val) for idx, val in zip(sparse_result.indices, sparse_result.values)}


class MSMarcoCrossEncoder(CrossEncoderProtocol):
    """
    Cross-Encoder for re-ranking hybrid search results to maximize precision.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CrossEncoder(model_name, device=self.device)
        
    def rerank(self, query: str, documents: list, top_k: int = 5) -> list:
        if not documents:
            return []
            
        # CrossEncoder expects list of [query, document_text]
        pairs = [[query, doc.content] for doc in documents]
        scores = self.model.predict(pairs)
        
        # Inject the cross-encoder score back into the domain model
        for doc, score in zip(documents, scores):
            doc.score = float(score)
            
        # Sort documents by cross-encoder score descending
        documents.sort(key=lambda x: x.score, reverse=True)
        
        # Return only the top_k best contexts to the LLM
        return documents[:top_k]
