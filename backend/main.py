"""
FastAPI Application Entry Point.
"""

import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.database.connection import init_db
from backend.utils.exceptions import ContractAnalyzerError
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production AI Contract Risk Analyzer SaaS API",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Open for development & frontend integration
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Logging Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] --> {request.method} {request.url.path}")
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(f"[{request_id}] <-- {response.status_code} ({elapsed:.1f}ms)")
        return response

    # Global Exception Handlers
    @app.exception_handler(ContractAnalyzerError)
    async def domain_exception_handler(request: Request, exc: ContractAnalyzerError):
        logger.error(f"Domain error on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unexpected error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "type": "InternalServerError"},
        )

    # Register Routers
    from backend.api.routes.admin import router as admin_router
    from backend.api.routes.analytics import router as analytics_router
    from backend.api.routes.analyze import router as analyze_router
    from backend.api.routes.auth import router as auth_router
    from backend.api.routes.chat import router as chat_router
    from backend.api.routes.contracts import router as contracts_router
    from backend.api.routes.upload import router as upload_router

    app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
    app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
    app.include_router(analyze_router, prefix="/api/v1", tags=["Analysis"])
    app.include_router(contracts_router, prefix="/api/v1", tags=["Contracts"])
    app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
    app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(admin_router, prefix="/api/v1", tags=["Admin"])

    # Health Check
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "llm_provider": settings.LLM_PROVIDER,
        }

    # Startup Event
    @app.on_event("startup")
    async def startup_event():
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        init_db()
        logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} initialized successfully.")

    return app


app = create_app()
