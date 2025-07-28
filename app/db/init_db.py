# import os
# import psycopg2
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# import logging

# logger = logging.getLogger(__name__)

# def create_database_if_not_exists():
#     """Create database if it doesn't exist"""
#     try:
#         # Connect to PostgreSQL server (not to a specific database)
#         conn = psycopg2.connect(
#             host=os.getenv("DB_HOST", "localhost"),
#             port=os.getenv("DB_PORT", "5432"),
#             user=os.getenv("DB_USER", "postgres"),
#             password=os.getenv("DB_PASSWORD", "1234")
#         )
#         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
#         cursor = conn.cursor()
        
#         # Check if database exists
#         db_name = os.getenv("DB_NAME", "docanalyzer")
#         cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
#         exists = cursor.fetchone()
        
#         if not exists:
#             cursor.execute(f'CREATE DATABASE "{db_name}"')
#             logger.info(f"Database '{db_name}' created successfully")
#         else:
#             logger.info(f"Database '{db_name}' already exists")
        
#         cursor.close()
#         conn.close()
        
#     except Exception as e:
#         logger.error(f"Error creating database: {e}")
#         raise

# def create_tables():
#     """Create all database tables"""
#     try:
#         database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/docanalyzer")
#         conn = psycopg2.connect(database_url)
#         cursor = conn.cursor()
        
#         # Enable UUID extension
#         cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
#         # Users table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 email VARCHAR(255) UNIQUE NOT NULL,
#                 password_hash VARCHAR(255) NOT NULL,
#                 first_name VARCHAR(100),
#                 last_name VARCHAR(100),
#                 is_email_verified BOOLEAN DEFAULT FALSE,
#                 email_verification_token VARCHAR(255),
#                 created_at TIMESTAMP DEFAULT NOW(),
#                 updated_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # Documents table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS documents (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 original_filename VARCHAR(255) NOT NULL,
#                 file_path_minio TEXT NOT NULL,
#                 file_size BIGINT NOT NULL,
#                 mime_type VARCHAR(100) NOT NULL,
#                 document_hash VARCHAR(64) UNIQUE,
#                 page_count INTEGER,
#                 language_detected VARCHAR(10),
#                 upload_timestamp TIMESTAMP DEFAULT NOW(),
#                 uploaded_by_user_id UUID,
#                 user_id UUID REFERENCES users(id) ON DELETE CASCADE,
#                 created_at TIMESTAMP DEFAULT NOW(),
#                 updated_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # Document processing table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS document_processing (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
#                 processing_status VARCHAR(50) NOT NULL,
#                 processing_errors JSONB,
#                 ocr_completed_at TIMESTAMP,
#                 classification_completed_at TIMESTAMP,
#                 summarization_completed_at TIMESTAMP,
#                 indexing_completed_at TIMESTAMP
#             );
#         """)
        
#         # Document content table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS document_content (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
#                 extracted_text TEXT,
#                 searchable_content TEXT,
#                 layout_sections JSONB,
#                 entities_extracted JSONB,
#                 ocr_confidence_score DECIMAL(5,4),
#                 has_tables BOOLEAN DEFAULT FALSE,
#                 has_images BOOLEAN DEFAULT FALSE
#             );
#         """)
        
#         # Document classifications table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS document_classifications (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
#                 document_type VARCHAR(50) NOT NULL,
#                 confidence_score DECIMAL(5,4) NOT NULL,
#                 model_version VARCHAR(20),
#                 classified_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # Document summaries table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS document_summaries (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
#                 summary_text TEXT NOT NULL,
#                 key_points JSONB,
#                 model_version VARCHAR(20),
#                 created_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # Document embeddings table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS document_embeddings (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
#                 chroma_collection_id VARCHAR(100),
#                 embedding_id VARCHAR(100),
#                 created_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # Document tags table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS document_tags (
#                 document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
#                 tag VARCHAR(50) NOT NULL,
#                 tag_type VARCHAR(20) DEFAULT 'user',
#                 PRIMARY KEY (document_id, tag)
#             );
#         """)
        
#         # Subscription plans table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS subscription_plans (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 name VARCHAR(50) NOT NULL,
#                 price_monthly DECIMAL(10,2) NOT NULL,
#                 price_yearly DECIMAL(10,2),
#                 features JSONB NOT NULL,
#                 is_active BOOLEAN DEFAULT TRUE,
#                 created_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # User subscriptions table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS user_subscriptions (
#                 id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#                 user_id UUID REFERENCES users(id) ON DELETE CASCADE,
#                 plan_id UUID REFERENCES subscription_plans(id),
#                 status VARCHAR(20) NOT NULL,
#                 started_at TIMESTAMP NOT NULL,
#                 expires_at TIMESTAMP,
#                 auto_renew BOOLEAN DEFAULT TRUE,
#                 created_at TIMESTAMP DEFAULT NOW()
#             );
#         """)
        
#         # User usage limits table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS user_usage_limits (
#                 user_id UUID REFERENCES users(id) ON DELETE CASCADE,
#                 documents_processed_monthly INTEGER DEFAULT 0,
#                 handwriting_recognition_used INTEGER DEFAULT 0,
#                 risk_assessments_used INTEGER DEFAULT 0,
#                 citation_analysis_used INTEGER DEFAULT 0,
#                 reset_date DATE NOT NULL,
#                 PRIMARY KEY (user_id)
#             );
#         """)
        
#         # Create indexes
#         cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON document_classifications(document_type);")
#         cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_timestamp);")
#         cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_status ON document_processing(processing_status);")
#         cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_search ON document_content USING gin(to_tsvector('english', searchable_content));")
        
#         conn.commit()
#         cursor.close()
#         conn.close()
        
#         logger.info("Database tables created successfully")
        
#     except Exception as e:
#         logger.error(f"Error creating tables: {e}")
#         raise

# def initialize_database():
#     """Initialize the complete database"""
#     try:
#         create_database_if_not_exists()
#         create_tables()
#         logger.info("Database initialization completed")
#     except Exception as e:
#         logger.error(f"Database initialization failed: {e}")
#         raise

# if __name__ == "__main__":
#     initialize_database()



import os
import psycopg2
import psycopg2.extras  # Add this import
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Register UUID adapter - ADD THIS LINE
psycopg2.extras.register_uuid()

logger = logging.getLogger(__name__)

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "1234")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        db_name = os.getenv("DB_NAME", "docanalyzer")
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def create_tables():
    """Create all database tables"""
    try:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/docanalyzer")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Enable UUID extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                is_email_verified BOOLEAN DEFAULT FALSE,
                email_verification_token VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                original_filename VARCHAR(255) NOT NULL,
                file_path_minio TEXT NOT NULL,
                file_size BIGINT NOT NULL,
                mime_type VARCHAR(100) NOT NULL,
                document_hash VARCHAR(64) UNIQUE,
                page_count INTEGER,
                language_detected VARCHAR(10),
                upload_timestamp TIMESTAMP DEFAULT NOW(),
                uploaded_by_user_id UUID,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Document processing table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_processing (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                processing_status VARCHAR(50) NOT NULL,
                processing_errors JSONB,
                ocr_completed_at TIMESTAMP,
                classification_completed_at TIMESTAMP,
                summarization_completed_at TIMESTAMP,
                indexing_completed_at TIMESTAMP
            );
        """)
        
        # Document content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_content (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                extracted_text TEXT,
                searchable_content TEXT,
                layout_sections JSONB,
                entities_extracted JSONB,
                ocr_confidence_score DECIMAL(5,4),
                has_tables BOOLEAN DEFAULT FALSE,
                has_images BOOLEAN DEFAULT FALSE
            );
        """)
        
        # Document classifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_classifications (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                document_type VARCHAR(50) NOT NULL,
                confidence_score DECIMAL(5,4) NOT NULL,
                model_version VARCHAR(20),
                classified_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Document summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_summaries (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                summary_text TEXT NOT NULL,
                key_points JSONB,
                model_version VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Document embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                chroma_collection_id VARCHAR(100),
                embedding_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Document tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                tag VARCHAR(50) NOT NULL,
                tag_type VARCHAR(20) DEFAULT 'user',
                PRIMARY KEY (document_id, tag)
            );
        """)
        
        # Subscription plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name VARCHAR(50) NOT NULL,
                price_monthly DECIMAL(10,2) NOT NULL,
                price_yearly DECIMAL(10,2),
                features JSONB NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # User subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                plan_id UUID REFERENCES subscription_plans(id),
                status VARCHAR(20) NOT NULL,
                started_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                auto_renew BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # User usage limits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_usage_limits (
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                documents_processed_monthly INTEGER DEFAULT 0,
                handwriting_recognition_used INTEGER DEFAULT 0,
                risk_assessments_used INTEGER DEFAULT 0,
                citation_analysis_used INTEGER DEFAULT 0,
                reset_date DATE NOT NULL,
                PRIMARY KEY (user_id)
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_type ON document_classifications(document_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_status ON document_processing(processing_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_search ON document_content USING gin(to_tsvector('english', searchable_content));")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def initialize_database():
    """Initialize the complete database"""
    try:
        create_database_if_not_exists()
        create_tables()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    initialize_database()
