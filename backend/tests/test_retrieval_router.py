import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.usecases.rag_usecase import ProcessClinicalQueryUseCase
from app.domain.models import MedicalQuery

class MockLLM:
    def generate(self, prompt: str) -> str:
        return "Mock response"

class MockDB:
    def search(self, *args, **kwargs):
        return []
    def hybrid_search(self, *args, **kwargs):
        return []

class MockEmbedder:
    def embed_query(self, text: str):
        return [0.0] * 384
    def embed_sparse(self, text: str):
        return {}

class MockEncoder:
    def rerank(self, *args, **kwargs):
        return []

def test_intent_classification():
    usecase = ProcessClinicalQueryUseCase(
        llm_provider=MockLLM(),
        vector_db=MockDB(),
        embedding_model=MockEmbedder(),
        cross_encoder=MockEncoder()
    )
    
    assert usecase.classify_intent("What is the drug class of Metformin?") == "identity"
    assert usecase.classify_intent("Who manufactures Advil?") == "identity"
    assert usecase.classify_intent("What are the brand names of Metformin?") == "identity"
    
    assert usecase.classify_intent("Contraindications of Metformin") == "clinical"
    assert usecase.classify_intent("Metformin side effects") == "clinical"
    assert usecase.classify_intent("What is the maximum daily dose of Lisinopril?") == "clinical"
