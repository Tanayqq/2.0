import structlog
from typing import List
from ...interfaces.embedding_provider import EmbeddingProvider

logger = structlog.get_logger()

class MedCPTProvider(EmbeddingProvider):
    """
    Embedding provider for MedCPT (medical text specialized embeddings).
    Requires PyTorch and transformers (lazy-loaded).
    """
    def __init__(self, model_name: str = "ncbi/MedCPT-Query-Encoder"):
        self.model_name = model_name
        logger.info("initializing_medcpt_provider", model=self.model_name)
        
        try:
            import torch
            from transformers import AutoTokenizer, AutoModel
            
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self.torch = torch
            
        except ImportError:
            raise ImportError(
                "PyTorch and transformers are required to use MedCPTProvider. "
                "Please run 'pip install torch transformers' or change the active "
                "embedding provider to 'fastembed' in the settings."
            )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Process in batches to avoid GPU/CPU memory overflow
        embeddings_list = []
        batch_size = 16
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            inputs = self.tokenizer(
                batch_texts, 
                truncation=True, 
                padding=True, 
                return_tensors='pt', 
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with self.torch.no_grad():
                outputs = self.model(**inputs)
                
            # Extract CLS token representation (standard for MedCPT)
            cls_embeddings = outputs.last_hidden_state[:, 0, :]
            embeddings_list.extend(cls_embeddings.cpu().numpy().tolist())
            
        return embeddings_list

    def get_dimension(self) -> int:
        return 768  # MedCPT query encoder outputs 768-dimensional vectors
