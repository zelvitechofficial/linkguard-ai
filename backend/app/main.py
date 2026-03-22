import os
# Fix OpenBLAS memory allocation error on Windows during reloads
os.environ['OPENBLAS_MAIN_FREE'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logger import setup_logger
from app.api.v1.endpoints import health, url, webhooks, chatbot, admin, usage
from app.db.session import engine
from app.services.ml_service import get_ml_service
from app.services.chatbot_service import get_chatbot_service

logger = setup_logger(__name__)

from app.db.base import Base
from app.models.user import User
from app.models.url_scan import URLScan
from app.models.chatbot_log import ChatbotLog

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Pre-warm singletons
    logger.info("Loading ML models...")
    get_ml_service()
    logger.info("Initialising chatbot service...")
    get_chatbot_service()
    logger.info("Startup complete.")

    yield

    logger.info("Shutting down — disposing DB engine.")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# --- Global Exception Handlers ---

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "success": False},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {request.method} {request.url} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred on the server.", "success": False},
    )

# --- Middleware ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---

@app.get("/")
async def root():
    return {
        "message": "LinkGuard AI Backend is running",
        "status": "online",
        "docs": "/docs"
    }

app.include_router(health.router,    prefix="/api/v1/healthcheck", tags=["healthcheck"])
app.include_router(url.router,       prefix="/api/v1/url",         tags=["url"])
app.include_router(webhooks.router,  prefix="/api/v1/auth/webhook", tags=["webhooks"])
app.include_router(chatbot.router,   prefix="/api/v1/chatbot",     tags=["chatbot"])
app.include_router(admin.router,     prefix="/api/v1/admin",       tags=["admin"])
app.include_router(usage.router,     prefix="/api/v1/usage",       tags=["usage"])
