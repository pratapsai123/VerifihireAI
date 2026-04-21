"""
DeepFace Proctoring Microservice — FastAPI Application

Main entry point that wires all routers, middleware, and lifecycle events.
Serves the testing dashboard UI from /static and / routes.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import API_PREFIX, CORS_ORIGINS
from app.models.database import close_db, get_pool
from app.routers import monitoring, registration, reports, session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("deepface")

# Path to static files
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown events."""
    # Startup
    logger.info("DeepFace Proctoring Microservice starting...")

    # Initialize PostgreSQL connection pool
    await get_pool()
    logger.info("PostgreSQL connection pool initialized.")

    # Pre-load models (optional — will lazy-load on first use otherwise)
    # Uncomment to pre-load at startup for faster first request:
    # logger.info("Pre-loading face recognition models...")
    # from deepface import DeepFace
    # DeepFace.build_model("ArcFace")
    # DeepFace.build_model("SFace")
    # logger.info("Models loaded.")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Database connection closed.")


# Create FastAPI app
app = FastAPI(
    title="DeepFace Proctoring Microservice",
    description=(
        "Production-grade face recognition, verification, and proctoring API. "
        "Supports real-time WebSocket monitoring with 19 integrated features."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# CORS Middleware
if "*" in CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(registration.router, prefix=API_PREFIX)
app.include_router(session.router, prefix=API_PREFIX)
app.include_router(monitoring.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)

# Mount static files (CSS, JS, assets)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Health check
@app.get(f"{API_PREFIX}/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "deepface-proctoring",
        "version": "1.0.0",
    }


# Serve the testing dashboard at root
@app.get("/")
async def serve_dashboard():
    """Serve the testing dashboard HTML page."""
    html_path = STATIC_DIR / "index.html"
    return FileResponse(str(html_path), media_type="text/html")
