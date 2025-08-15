import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class manages all configuration settings for the application,
    including API keys, database settings, and service configurations.
    """
    
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
    
    # Additional Database Settings (from .env)
    DB_HOST: Optional[str] = Field(None, description="Database host (alternative)")
    DB_PORT: Optional[str] = Field(None, description="Database port (alternative)")
    DB_USER: Optional[str] = Field(None, description="Database user (alternative)")
    DB_PASSWORD: Optional[str] = Field(None, description="Database password (alternative)")
    DB_NAME: Optional[str] = Field(None, description="Database name (alternative)")
    
    # Additional API Settings (from .env)
    API_HOST: Optional[str] = Field(None, description="API host")
    API_PORT: Optional[str] = Field(None, description="API port")
    
    # Vector Database Settings
    VECTOR_DB_PATH: str = Field("./chroma_db", description="ChromaDB storage path")
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
    DEFAULT_LLM_PROVIDER: str = Field("gemini", description="Default LLM provider")
    DEFAULT_LLM_MODEL: str = Field("gemini-1.5-flash", description="Default LLM model")
    DEFAULT_TEMPERATURE: float = Field(0.7, description="Default LLM temperature")
    DEFAULT_MAX_TOKENS: int = Field(1000, description="Default max tokens")
    
    # Security Settings
    SECRET_KEY: str = Field("your-secret-key-here", description="Secret key for JWT")
    ALGORITHM: str = Field("HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="JWT token expiry minutes")
    
    # CORS Settings
    CORS_ORIGINS: list = Field(
        ["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # Logging Settings
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FILE: str = Field("logs/app.log", description="Log file path")
    
    # File Upload Settings
    UPLOAD_DIR: Optional[str] = Field(None, description="Upload directory")
    MAX_FILE_SIZE: int = Field(10 * 1024 * 1024, description="Maximum file size in bytes (10MB)")
    ALLOWED_FILE_TYPES: list = Field(
        [".pdf", ".txt", ".docx", ".doc", ".md"],
        description="Allowed file types"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(60, description="Rate limit per minute")
    
    # Cache Settings
    CACHE_TTL: int = Field(3600, description="Cache TTL in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from .env file


# Create global settings instance
settings = Settings()


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
