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

app = FastAPI(title=settings.APP_NAME)

# Secure CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ALLOWED_ORIGINS = [
    "http://localhost:5173", # Local Vite dev server
    FRONTEND_URL             # Production Vercel domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

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
