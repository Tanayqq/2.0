from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.core.config import settings
import structlog
import uuid
import time
import os

# Initialize structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

app = FastAPI(title=settings.APP_NAME, version="5.0.1")

# Secure CORS Configuration
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
logger.info("Allowed CORS Origins:\\n" + "\\n".join(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("prewarming_models_start")
    try:
        from app.api.dependencies import get_embedding_model, get_vector_db
        embed = get_embedding_model()
        embed.embed_query("warmup query")
        vdb = get_vector_db()
        logger.info("prewarming_models_complete")
    except Exception as e:
        logger.error("prewarming_models_error", error=str(e))

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        url=str(request.url.path),
    )
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info("request_completed", status_code=response.status_code, latency_sec=round(process_time, 4))
    
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(router, prefix="/api/v1")
