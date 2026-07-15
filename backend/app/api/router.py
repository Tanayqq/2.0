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

import traceback
from fastapi.responses import JSONResponse

@router.post("/query", response_model=AnswerResponse)
def handle_query(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    try:
        return usecase.execute(query)
    except Exception as e:
        logger.exception("Query failed", error=str(e))
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            return JSONResponse(status_code=429, content={"success": False, "error": error_msg})
        return JSONResponse(status_code=500, content={"success": False, "error": "Internal Server Error"})

@router.post("/debug/retrieval")
def debug_retrieval(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    """Retrieval Inspector Endpoint: View chunks retrieved before generation."""
    return usecase.get_debug_retrieval(query)

@router.post("/debug/prompt")
def debug_prompt(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    """Prompt Inspector Endpoint: View the exact prompt to be sent to the LLM."""
    return usecase.get_debug_prompt(query)

@router.post("/debug/trace")
def debug_trace(query: MedicalQuery, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    """Diagnostic Trace Endpoint: View complete end-to-end RAG trace."""
    return usecase.get_debug_trace(query)

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/identity/{drug}")
def get_identity_profile(drug: str, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    entity_id = usecase.profile_store.get_entity_by_alias(drug)
    if not entity_id:
        from app.usecases.drug_resolver import DrugNameResolver
        generic = DrugNameResolver.resolve(drug)
        if generic:
            entity_id = f"drug:{generic}"
            
    if entity_id:
        profile = usecase.profile_store.get_profile(entity_id, "identity", authority="FDA")
        if profile:
            return {"success": True, "profile": profile}
    return JSONResponse(status_code=404, content={"success": False, "error": f"Identity profile not found for '{drug}'"})

@router.get("/clinical/{drug}")
def get_clinical_profile(drug: str, usecase: ProcessClinicalQueryUseCase = Depends(get_usecase)):
    entity_id = usecase.profile_store.get_entity_by_alias(drug)
    if not entity_id:
        from app.usecases.drug_resolver import DrugNameResolver
        generic = DrugNameResolver.resolve(drug)
        if generic:
            entity_id = f"drug:{generic}"
            
    if entity_id:
        profile = usecase.profile_store.get_profile(entity_id, "clinical", authority="FDA")
        if profile:
            return {"success": True, "profile": profile}
    return JSONResponse(status_code=404, content={"success": False, "error": f"Clinical profile not found for '{drug}'"})

@router.get("/version")
def version_check():
    """
    Returns the deployed commit hash and active config values.
    Use this to verify what code Render is actually running.
    Check: GET /api/v1/version
    """
    import subprocess
    from app.core.config import settings
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        commit = os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_COMMIT", "unknown"))
    return {
        "version": settings.APP_VERSION,
        "git_commit": commit,
        "active_config": {
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
            "strict_citation_validation_action": settings.STRICT_CITATION_VALIDATION_ACTION,
            "default_top_k": settings.DEFAULT_TOP_K,
            "multi_section_top_k": settings.MULTI_SECTION_TOP_K,
            "max_context_chunks": settings.MAX_CONTEXT_CHUNKS,
            "active_llm_provider": settings.ACTIVE_LLM_PROVIDER,
        }
    }
