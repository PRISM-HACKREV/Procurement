"""
PRISMA Procurement & Supplier Integration Layer
Main FastAPI Application

Provides mock procurement APIs for supplier search, quotes, routing, and health checks.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from src.core.config import settings
from src.domain.schemas import HealthStatus
from src.routes import suppliers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-driven procurement and supplier integration layer for PRISMA supply chain optimization",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(suppliers.router)


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info(f"🚀 PRISMA Procurement API starting...")
    logger.info(f"   Mode: {settings.SOURCE_MODE}")
    logger.info(f"   Port: {settings.API_PORT}")
    logger.info(f"   Cache TTL: {settings.CACHE_TTL_HOURS}h")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("👋 PRISMA Procurement API shutting down...")


@app.get("/", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns basic service status and configuration information.
    """
    return HealthStatus(
        status="healthy",
        version=settings.API_VERSION,
        mode=settings.SOURCE_MODE,
        timestamp=datetime.utcnow()
    )


@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health():
    """
    Detailed health check endpoint
    
    Returns service health status with timestamp.
    """
    return HealthStatus(
        status="healthy",
        version=settings.API_VERSION,
        mode=settings.SOURCE_MODE,
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

