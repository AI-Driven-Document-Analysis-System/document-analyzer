# import os
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from psycopg2.pool import ThreadedConnectionPool
# from contextlib import contextmanager
# import logging

# logger = logging.getLogger(__name__)

# class DatabaseManager:
#     def __init__(self):
#         self.connection_pool = None
#         self._initialize_pool()
    
#     def _initialize_pool(self):
#         """Initialize the connection pool"""
#         try:
#             # database_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/docanalyzer")
#             database_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/docanalyzer")

            
#             # Parse the database URL
#             if database_url.startswith("postgresql://"):
#                 self.connection_pool = ThreadedConnectionPool(
#                     minconn=1,
#                     maxconn=20,
#                     dsn=database_url
#                 )
#                 logger.info("Database connection pool initialized successfully")
#             else:
#                 raise ValueError("Invalid database URL format")
                
#         except Exception as e:
#             logger.error(f"Failed to initialize database connection pool: {e}")
#             raise
    
#     @contextmanager
#     def get_connection(self):
#         """Get a connection from the pool"""
#         connection = None
#         try:
#             connection = self.connection_pool.getconn()
#             yield connection
#         except Exception as e:
#             if connection:
#                 connection.rollback()
#             logger.error(f"Database connection error: {e}")
#             raise
#         finally:
#             if connection:
#                 self.connection_pool.putconn(connection)
    
#     @contextmanager
#     def get_cursor(self, commit=True):
#         """Get a cursor with automatic connection management"""
#         with self.get_connection() as connection:
#             cursor = connection.cursor(cursor_factory=RealDictCursor)
#             try:
#                 yield cursor
#                 if commit:
#                     connection.commit()
#             except Exception as e:
#                 connection.rollback()
#                 logger.error(f"Database cursor error: {e}")
#                 raise
#             finally:
#                 cursor.close()
    
#     def execute_query(self, query, params=None, fetch=False):
#         """Execute a query and optionally fetch results"""
#         with self.get_cursor() as cursor:
#             cursor.execute(query, params)
#             if fetch:
#                 return cursor.fetchall()
#             return cursor.rowcount
    
#     def execute_one(self, query, params=None):
#         """Execute a query and fetch one result"""
#         with self.get_cursor() as cursor:
#             cursor.execute(query, params)
#             return cursor.fetchone()
    
#     def close_pool(self):
#         """Close all connections in the pool"""
#         if self.connection_pool:
#             self.connection_pool.closeall()
#             logger.info("Database connection pool closed")

# # Global database manager instance
# db_manager = DatabaseManager()

# def get_db():
#     """Dependency to get database connection"""
#     return db_manager





import os
import psycopg2
import psycopg2.extras  # Add this import
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging

# Register UUID adapter - ADD THIS LINE
psycopg2.extras.register_uuid()

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            # database_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/docanalyzer")
            database_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/docanalyzer")

            
            # Parse the database URL
            if database_url.startswith("postgresql://"):
                self.connection_pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=database_url
                )
                logger.info("Database connection pool initialized successfully")
            else:
                raise ValueError("Invalid database URL format")
                
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    @contextmanager
    def get_cursor(self, commit=True):
        """Get a cursor with automatic connection management"""
        with self.get_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                if commit:
                    connection.commit()
            except Exception as e:
                connection.rollback()
                logger.error(f"Database cursor error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and optionally fetch results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount
    
    def execute_one(self, query, params=None):
        """Execute a query and fetch one result"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def close_pool(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_db():
    """Dependency to get database connection"""
    return db_manager