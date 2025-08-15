
import os
import psycopg2
import psycopg2.extras  # Add this import
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging
from dotenv import load_dotenv
import time
from typing import Optional

# Load environment variables from .env file
load_dotenv()


# Register UUID adapter - ADD THIS LINE
psycopg2.extras.register_uuid()

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            database_url = os.getenv("DATABASE_URL")
            
            if not database_url:
                logger.error("DATABASE_URL environment variable is not set")
                raise ValueError("DATABASE_URL not configured")
            
            # Parse the database URL
            if database_url.startswith("postgresql://"):
                logger.info(f"Initializing connection pool with: {database_url[:20]}...")
                
                # Test connection before creating pool
                try:
                    import psycopg2
                    test_conn = psycopg2.connect(database_url)
                    test_conn.close()
                    logger.info("Database connection test successful")
                except Exception as e:
                    logger.error(f"Database connection test failed: {e}")
                    raise
                
                self.connection_pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=database_url
                )
                logger.info("Database connection pool initialized successfully")
            else:
                raise ValueError(f"Invalid database URL format: {database_url}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            # Don't raise here, allow the app to start but mark pool as failed
            self.connection_pool = None
    
    def _check_connection_health(self, connection) -> bool:
        """Check if a connection is still healthy"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception:
            return False
    
    def _get_healthy_connection(self):
        """Get a healthy connection from the pool, with retries"""
        if not self.connection_pool:
            raise Exception("Connection pool not initialized")
            
        for attempt in range(self.max_retries):
            try:
                connection = self.connection_pool.getconn()
                if self._check_connection_health(connection):
                    return connection
                else:
                    # Connection is stale, return it and try again
                    try:
                        self.connection_pool.putconn(connection)
                    except Exception as e:
                        logger.warning(f"Error returning stale connection: {e}")
                    logger.warning(f"Stale connection detected, retrying... (attempt {attempt + 1})")
                    time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Failed to get connection (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        # If we get here, all retries failed
        raise Exception("Failed to get healthy database connection after all retries")
    
    def _perform_health_check(self):
        """Perform periodic health check on the pool"""
        current_time = time.time()
        if current_time - self.last_health_check > self.health_check_interval:
            try:
                with self.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                self.last_health_check = current_time
                logger.debug("Database health check passed")
            except Exception as e:
                logger.warning(f"Database health check failed: {e}")
                self._reinitialize_pool()
    
    def _reinitialize_pool(self):
        """Reinitialize the connection pool if it's in a bad state"""
        try:
            logger.info("Reinitializing database connection pool...")
            if self.connection_pool:
                try:
                    self.connection_pool.closeall()
                except Exception as e:
                    logger.warning(f"Error closing old pool: {e}")
            
            self.connection_pool = None
            self.last_health_check = 0
            self._initialize_pool()
            
            if self.connection_pool:
                logger.info("Database connection pool reinitialized successfully")
            else:
                logger.error("Failed to reinitialize connection pool")
                
        except Exception as e:
            logger.error(f"Failed to reinitialize connection pool: {e}")
            self.connection_pool = None
    
    def initialize_pool(self):
        """Manually initialize the connection pool"""
        try:
            if self.connection_pool:
                logger.info("Connection pool already exists, closing first...")
                self.connection_pool.closeall()
            
            self._initialize_pool()
            return self.connection_pool is not None
        except Exception as e:
            logger.error(f"Manual pool initialization failed: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool with health checks"""
        connection = None
        try:
            # Perform periodic health check
            self._perform_health_check()
            
            # Get a healthy connection
            connection = self._get_healthy_connection()
            yield connection
        except Exception as e:
            if connection:
                try:
                    connection.rollback()
                except Exception:
                    pass
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                try:
                    self.connection_pool.putconn(connection)
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")
    
    @contextmanager
    def get_cursor(self, commit=True):
        """Get a cursor with automatic connection management and health checks"""
        with self.get_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                if commit:
                    connection.commit()
            except Exception as e:
                try:
                    connection.rollback()
                except Exception:
                    pass
                logger.error(f"Database cursor error: {e}")
                raise
            finally:
                try:
                    cursor.close()
                except Exception:
                    pass
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query with automatic retry and health checks"""
        for attempt in range(self.max_retries):
            try:
                with self.get_cursor() as cursor:
                    cursor.execute(query, params)
                    if fetch:
                        return cursor.fetchall()
                    return cursor.rowcount
            except psycopg2.OperationalError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"Database operation failed after all retries: {e}")
                    raise
            except Exception as e:
                logger.error(f"Database operation error: {e}")
                raise
    
    def execute_one(self, query, params=None):
        """Execute a query and fetch one result with automatic retry"""
        for attempt in range(self.max_retries):
            try:
                with self.get_cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchone()
            except psycopg2.OperationalError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"Database operation failed after all retries: {e}")
                    raise
            except Exception as e:
                logger.error(f"Database operation error: {e}")
                raise
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            if not self.connection_pool:
                logger.warning("Connection pool not initialized")
                return False
                
            # Quick check without full connection cycle
            try:
                connection = self.connection_pool.getconn()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    self.connection_pool.putconn(connection)
                    return result[0] == 1
            except Exception as e:
                logger.warning(f"Quick connection test failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_pool_status(self) -> dict:
        """Get connection pool status"""
        try:
            if not self.connection_pool:
                return {
                    "status": "pool_not_initialized",
                    "error": "DATABASE_URL not configured or connection failed"
                }
            
            return {
                "status": "initialized",
                "pool_size": self.connection_pool.maxconn,
                "active_connections": self.connection_pool.maxconn - self.connection_pool.minconn,
                "last_health_check": self.last_health_check,
                "connection_healthy": self.test_connection()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def is_initialized(self) -> bool:
        """Check if the connection pool is properly initialized"""
        return self.connection_pool is not None
    
    def close_pool(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            try:
                self.connection_pool.closeall()
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Dependency to get database connection"""
    return db_manager

