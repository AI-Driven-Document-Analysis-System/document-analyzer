from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from .api import auth, documents
from .core.database import db_manager

# Load environment variables early
load_dotenv()

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DocAnalyzer API (Minimal)",
    description="AI-powered document analysis platform - Core functionality only",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Include only essential routers
app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DocAnalyzer API (Minimal)",
        "version": "1.0.0",
        "status": "running",
        "note": "Core functionality only - AI/ML features disabled"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("DocAnalyzer API (Minimal) starting up...")
    
    # Test database connection
    try:
        if db_manager.test_connection():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed")
    except Exception as e:
        logger.warning(f"Database connection warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("DocAnalyzer API (Minimal) shutting down...")
    
    # Close database connections
    try:
        db_manager.close_pool()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )