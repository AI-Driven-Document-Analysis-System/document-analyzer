from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
import asyncio
from datetime import datetime
from .api import auth, summarization, documents, chat, analytics, document_selections, chat_streaming  # Add chat_streaming import
from .core.database import db_manager
from .db.init_db import create_tables
from .api import profile

# Load environment variables early
load_dotenv()

# Configure logging
os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists
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
    title="DocAnalyzer API",
    description="AI-powered document analysis platform",
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
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "127.0.0.1:3000"]
)

# Include routers (FIXED - removed duplicates, added documents)
app.include_router(auth.router, prefix="/api")
app.include_router(summarization.router, prefix="/api")
app.include_router(documents.router, prefix="/api")  # Add this line
app.include_router(chat.router, prefix="/api")  # Add chat router
app.include_router(analytics.router, prefix="/api")  # Add analytics router
app.include_router(profile.router, prefix="/api")
app.include_router(document_selections.router, prefix="/api")  # Add document selections router
app.include_router(chat_streaming.router, prefix="/api")  # Add streaming chat router


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DocAnalyzer API",
        "version": "1.0.0",
        "status": "running"
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
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Don't crash the server, just return unhealthy status
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("DocAnalyzer API starting up...")

    # Initialize database tables if DATABASE_URL is configured
    try:
        if os.getenv("DATABASE_URL"):
            create_tables()
            logger.info("Database tables ensured")
        else:
            logger.info("DATABASE_URL not set; skipping table initialization")

        # Start background database monitoring task
        try:
            asyncio.create_task(database_monitor_task())
            logger.info("Database monitoring task started")
        except Exception as e:
            logger.warning(f"Failed to start database monitoring: {e}")

        # Start title generation listener
        try:
            from app.services.chatbot.title_generation.title_listener import start_title_listener
            asyncio.create_task(start_title_listener())
            logger.info("Title generation listener started")
        except Exception as e:
            logger.warning(f"Failed to start title listener: {e}")

    except Exception as e:
        logger.warning(f"Startup DB init warning: {e}")
        # Don't crash the server if DB init fails


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("DocAnalyzer API shutting down...")

    # Close database connections
    try:
        db_manager.close_pool()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


async def database_monitor_task():
    """Background task to monitor database health and clean up connections"""
    while True:
        try:
            # Check database health every 5 minutes
            await asyncio.sleep(300)  # 5 minutes

            # Test connection and log status
            if db_manager.test_connection():
                logger.debug("Database health check passed")
            else:
                logger.warning("Database health check failed, attempting reconnection...")
                try:
                    # Use the safer public method instead of private method
                    success = db_manager.initialize_pool()
                    if success:
                        logger.info("Database reconnection successful")
                    else:
                        logger.error("Database reconnection failed")
                except Exception as e:
                    logger.error(f"Database reconnection failed: {e}")

        except Exception as e:
            logger.error(f"Database monitoring task error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to True for development
        log_level="info"
    )