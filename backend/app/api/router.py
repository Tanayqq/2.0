from fastapi import APIRouter, Depends
from app.domain.models import MedicalQuery, AnswerResponse
from app.usecases.rag_usecase import ProcessClinicalQueryUseCase
from app.api.dependencies import get_llm_provider, get_vector_db, get_embedding_model, get_cross_encoder
import structlog
import os

router = APIRouter()
logger = structlog.get_logger()

def get_usecase(
    llm=Depends(get_llm_provider),
    db=Depends(get_vector_db),
    embed=Depends(get_embedding_model),
    cross=Depends(get_cross_encoder)
):
    return ProcessClinicalQueryUseCase(llm_provider=llm, vector_db=db, embedding_model=embed, cross_encoder=cross)

@router.post("/query", response_model=AnswerResponse)
def handle_query(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    return usecase.execute(query)

@router.post("/debug/retrieval")
def debug_retrieval(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    """Retrieval Inspector Endpoint: View chunks retrieved before generation."""
    return usecase.get_debug_retrieval(query)

@router.post("/debug/prompt")
def debug_prompt(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    """Prompt Inspector Endpoint: View the exact prompt to be sent to the LLM."""
    return usecase.get_debug_prompt(query)

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "medref-api"}

@router.get("/version")
def version_check():
    return {"version": os.getenv("APP_VERSION", "1.0.0-dev")}
