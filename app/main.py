from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from app.api.routes import include_routes
from app.database import create_tables
from app.scheduler.poller import task_scheduler
from app.utils.logger import get_logger
from app.redis_client import redis_client

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting Agworld Reporter application")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Test Redis connection
        if redis_client.ping():
            logger.info("Redis connection established")
        else:
            logger.warning("Redis connection failed")
        
        # Start task scheduler
        task_scheduler.start()
        logger.info("Task scheduler started")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agworld Reporter application")
    try:
        task_scheduler.shutdown()
        logger.info("Task scheduler stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="Agworld Reporter API",
    description="A FastAPI-based service for integrating with Agworld, processing data, generating reports, and sending notifications.",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
include_routes(app)

@app.get("/")
def read_root():
    """Root endpoint with basic information"""
    return {
        "message": "Agworld Reporter API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/api/v1/health",
            "reports": "/api/v1/reports",
            "scheduler": "/api/v1/scheduler/status",
            "polling": "/api/v1/polling/status",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
