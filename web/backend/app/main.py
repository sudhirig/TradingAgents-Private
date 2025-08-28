#!/usr/bin/env python3
"""
TradingAgents Web Backend - FastAPI Application
Main application entry point with middleware, routing, and WebSocket support
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime

# Import project modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from load_env import load_env

# Import routers
from .routers import analysis, config, websocket, metrics

# Import services
from .services.websocket_manager import websocket_manager
from .services.analysis_service import analysis_service

# Import utilities
from .utils.performance import performance_monitor
from .utils.security import SecurityHeaders, check_rate_limit

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from load_env import load_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("web_backend.log")
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting TradingAgents Web Backend")
    
    # Environment variables are auto-loaded by load_env module
    logger.info("✅ Environment variables loaded")
    
    # Validate required environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {missing_vars}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down TradingAgents Web Backend")

# Create FastAPI application
app = FastAPI(
    title="TradingAgents Web API",
    description="Real-time financial analysis with multi-agent LLM system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "testserver"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    import time
    import uuid
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url} - Request ID: {request_id}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"📤 {request.method} {request.url} - {response.status_code} - {process_time:.3f}s - Request ID: {request_id}")
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"💥 {request.method} {request.url} - ERROR - {process_time:.3f}s - Request ID: {request_id} - {str(e)}")
        raise

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TradingAgents Web Backend",
        "version": "1.0.0",
        "timestamp": "2025-08-28T02:39:40+05:30"
    }

# Root endpoint
@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "TradingAgents Web API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Setup API routers
def setup_routers():
    """Setup API routers"""
    try:
        from app.routers import analysis, config, websocket, metrics
        app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
        app.include_router(config.router, prefix="/api/config", tags=["config"])
        app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
        app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
        logger.info("✅ API routers configured")
    except Exception as e:
        logger.error(f"❌ Failed to setup routers: {e}")

# Setup routers immediately
setup_routers()

def create_app() -> FastAPI:
    """Factory function to create FastAPI app"""
    return app

if __name__ == "__main__":
    
    # Development server configuration
    config = {
        "host": "0.0.0.0",
        "port": 8001,
        "reload": True,
        "log_level": "info"
    }
    
    logger.info(f"🌐 Starting server on {config['host']}:{config['port']}")
    logger.info(f"📚 API documentation available at http://{config['host']}:{config['port']}/docs")
    
    uvicorn.run(
        "main:app",
        **config
    )
