import os
import json
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class manages all configuration settings for the application,
    including API keys, database settings, and service configurations.
    """
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # This allows extra fields without raising errors
        protected_namespaces=()  # This fixes the model_ namespace warning
    )
    
    # Application Settings
    APP_NAME: str = Field("DocAnalyzer API", description="Application name")
    APP_VERSION: str = Field("1.0.0", description="Application version")
    DEBUG: bool = Field(False, description="Debug mode")
    
    # Server Settings
    HOST: str = Field("0.0.0.0", description="Server host")
    PORT: int = Field(8000, description="Server port")
    
    # Database Settings
    DATABASE_URL: Optional[str] = Field(None, description="Database connection URL")
    DATABASE_HOST: str = Field("localhost", description="Database host")
    DATABASE_PORT: int = Field(5432, description="Database port")
    DATABASE_NAME: str = Field("docanalyzer", description="Database name")
    DATABASE_USER: str = Field("postgres", description="Database user")
    DATABASE_PASSWORD: str = Field("", description="Database password")
    
    # Additional Database Settings (from .env) - lowercase versions for compatibility
    db_host: str = Field("localhost", description="Database host (alternative)")
    db_port: int = Field(5432, description="Database port (alternative)")
    db_user: str = Field("postgres", description="Database user (alternative)")
    db_password: str = Field("password", description="Database password (alternative)")
    db_name: str = Field("document_analyzer", description="Database name (alternative)")
    database_url: Optional[str] = Field(None, description="Database URL (alternative)")
    
    # Additional API Settings (from .env)
    api_host: str = Field("0.0.0.0", description="API host (alternative)")
    api_port: int = Field(8000, description="API port (alternative)")
    
    # Vector Database Settings
    VECTOR_DB_PATH: str = Field("./data/chroma_db", description="ChromaDB storage path")
    COLLECTION_NAME: str = Field("documents", description="ChromaDB collection name")
    
    # Document Processing Settings
    CHUNK_SIZE: int = Field(1000, description="Document chunk size")
    CHUNK_OVERLAP: int = Field(200, description="Document chunk overlap")
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", description="Sentence transformer model")
    MAX_HISTORY_LENGTH: int = Field(10, description="Maximum conversation history length")
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    GEMINI_API_KEY: Optional[str] = Field(None, description="Google Gemini API key")
    GROQ_API_KEY: Optional[str] = Field(None, description="Groq API key")
    
    # LLM Default Settings
    DEFAULT_LLM_PROVIDER: str = Field("groq", description="Default LLM provider")
    DEFAULT_LLM_MODEL: str = Field("gemini-1.5-flash", description="Default LLM model")
    DEFAULT_TEMPERATURE: float = Field(0.7, description="Default LLM temperature")
    DEFAULT_MAX_TOKENS: int = Field(1000, description="Default max tokens")
    
    # Security Settings
    SECRET_KEY: str = Field("your-secret-key-change-in-production", description="Secret key for JWT")
    ALGORITHM: str = Field("HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="JWT token expiry minutes")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # Logging Settings
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FILE: str = Field("logs/app.log", description="Log file path")
    
    # File Upload Settings
    UPLOAD_DIR: str = Field("storage/documents", description="Upload directory")
    MAX_FILE_SIZE: int = Field(10 * 1024 * 1024, description="Maximum file size in bytes (10MB)")
    ALLOWED_FILE_TYPES: List[str] = Field(
        [".pdf", ".txt", ".docx", ".doc", ".md"],
        description="Allowed file types"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, description="Rate limit per minute")
    
    # Cache Settings
    CACHE_TTL: int = Field(3600, description="Cache TTL in seconds")
    
    # MinIO Settings (from friend's version)
    MINIO_ENDPOINT: str = Field("localhost:9000", description="MinIO endpoint")
    MINIO_ACCESS_KEY: str = Field("minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field("minioadmin", description="MinIO secret key")
    MINIO_BUCKET_NAME: str = Field("documents", description="MinIO bucket name")
    MINIO_SECURE: bool = Field(False, description="MinIO secure connection")
    
    # AI/ML Settings (from friend's version)
    MODEL_NAME: str = Field("gpt-3.5-turbo", description="Default model name")
    MAX_TOKENS: int = Field(1000, description="Maximum tokens")
    TEMPERATURE: float = Field(0.7, description="Model temperature")
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle JSON string from environment variable
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated string
                return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    def get_database_url(self) -> str:
        """Get the complete database URL"""
        # Try uppercase settings first, then fallback to lowercase
        if self.DATABASE_URL:
            return self.DATABASE_URL
        elif self.database_url:
            return self.database_url
        
        # Use uppercase settings if available, otherwise lowercase
        host = self.DATABASE_HOST if hasattr(self, 'DATABASE_HOST') else self.db_host
        port = self.DATABASE_PORT if hasattr(self, 'DATABASE_PORT') else self.db_port
        user = self.DATABASE_USER if hasattr(self, 'DATABASE_USER') else self.db_user
        password = self.DATABASE_PASSWORD if hasattr(self, 'DATABASE_PASSWORD') else self.db_password
        name = self.DATABASE_NAME if hasattr(self, 'DATABASE_NAME') else self.db_name
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"


# Create global settings instance
settings = Settings()

# Print database URL for debugging
print(f"DB URL used by FastAPI: {settings.get_database_url()}")


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings: The global settings instance
    """
    return settings


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    VECTOR_DB_PATH: str = "./test_data/chroma_db"
    DATABASE_NAME: str = "test_docanalyzer"


def get_settings_by_env(env: str = None) -> Settings:
    """
    Get settings based on environment.
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Settings: Environment-specific settings
    """
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the main settings instance
__all__ = ["settings", "get_settings", "get_settings_by_env", "Settings"]
