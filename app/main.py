# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware
# import logging
# import os
# from .api import auth, summarization, documents  # Add documents import
# from .api import auth
# from .core.database import db_manager



# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler("logs/app.log"),
#         logging.StreamHandler()
#     ]
# )

# logger = logging.getLogger(__name__)

# # Create FastAPI app
# app = FastAPI(
#     title="DocAnalyzer API",
#     description="AI-powered document analysis platform",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# app.include_router(auth.router, prefix="/api")
# app.include_router(summarization.router, prefix="/api")  # Add summarization router
# app.include_router(documents.router, prefix="/api")  # Add documents router

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Add trusted host middleware
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
# )

# # Include routers
# app.include_router(auth.router, prefix="/api")

# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": "DocAnalyzer API",
#         "version": "1.0.0",
#         "status": "running"
#     }

# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     try:
#         # Test database connection
#         with db_manager.get_connection() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute("SELECT 1")
#                 cursor.fetchone()
        
#         return {
#             "status": "healthy",
#             "database": "connected",
#             "timestamp": "2024-01-01T00:00:00Z"
#         }
#     except Exception as e:
#         logger.error(f"Health check failed: {e}")
#         raise HTTPException(status_code=503, detail="Service unavailable")

# @app.on_event("startup")
# async def startup_event():
#     """Startup event handler"""
#     logger.info("DocAnalyzer API starting up...")
    
#     # Initialize database tables if needed
#     try:
#         # You can add database initialization logic here
#         logger.info("Database connection verified")
#     except Exception as e:
#         logger.error(f"Startup error: {e}")
#         raise

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Shutdown event handler"""
#     logger.info("DocAnalyzer API shutting down...")
    
#     # Close database connections
#     try:
#         db_manager.close_pool()
#         logger.info("Database connections closed")
#     except Exception as e:
#         logger.error(f"Shutdown error: {e}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=False,  # Set to True for development
#         log_level="info"
#     )




from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from .api import auth, summarization, documents  # Add documents import
from .core.database import db_manager

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
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Include routers (FIXED - removed duplicates, added documents)
app.include_router(auth.router, prefix="/api")
app.include_router(summarization.router, prefix="/api")
app.include_router(documents.router, prefix="/api")  # Add this line

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
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("DocAnalyzer API starting up...")
    
    # Initialize database tables if needed
    try:
        # You can add database initialization logic here
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to True for development
        log_level="info"
    )