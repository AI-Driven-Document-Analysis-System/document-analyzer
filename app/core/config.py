import os
import json
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""
	Unified application settings supporting both configurations.
	- Accepts multiple env var variants (uppercase/lowercase and DB_* synonyms)
	- Includes conversation summarization + MinIO + AI/ML compatibility fields
	- Robust CORS and boolean parsing
	"""

	# Pydantic v2 configuration
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,   # accept both uppercase/lowercase env names
		extra="ignore",         # ignore unknown env vars
		protected_namespaces=() # avoid model_ namespace warnings
	)

	# Application Settings
	APP_NAME: str = Field("DocAnalyzer API", description="Application name")
	APP_VERSION: str = Field("1.0.0", description="Application version")
	DEBUG: bool = Field(False, description="Debug mode")

	# Server Settings
	HOST: str = Field("0.0.0.0", description="Server host")
	PORT: int = Field(8000, description="Server port")

	# Database Settings (primary)
	DATABASE_URL: Optional[str] = Field(None, description="Database connection URL")
	DATABASE_HOST: str = Field("localhost", description="Database host")
	DATABASE_PORT: int = Field(5432, description="Database port")
	DATABASE_NAME: str = Field("docanalyzer", description="Database name")
	DATABASE_USER: str = Field("postgres", description="Database user")
	DATABASE_PASSWORD: str = Field("", description="Database password")

	# Database Settings (compatibility: uppercase DB_* and lowercase)
	DB_HOST: Optional[str] = Field(None, description="Database host (alternative)")
	DB_PORT: Optional[str] = Field(None, description="Database port (alternative)")
	DB_USER: Optional[str] = Field(None, description="Database user (alternative)")
	DB_PASSWORD: Optional[str] = Field(None, description="Database password (alternative)")
	DB_NAME: Optional[str] = Field(None, description="Database name (alternative)")
	database_url: Optional[str] = Field(None, description="Database URL (alternative, lowercase)")
	db_host: str = Field("localhost", description="Database host (lowercase alternative)")
	db_port: int = Field(5432, description="Database port (lowercase alternative)")
	db_user: str = Field("postgres", description="Database user (lowercase alternative)")
	db_password: str = Field("password", description="Database password (lowercase alternative)")
	db_name: str = Field("document_analyzer", description="Database name (lowercase alternative)")

	API_HOST: Optional[str] = Field(None, description="API host")
	API_PORT: Optional[int] = Field(None, description="API port")
	api_host: str = Field("0.0.0.0", description="API host (lowercase alternative)")
	api_port: int = Field(8000, description="API port (lowercase alternative)")

	# Vector Database Settings
	VECTOR_DB_PATH: str = Field("./data/chroma_db", description="ChromaDB storage path")
	COLLECTION_NAME: str = Field("documents", description="ChromaDB collection name")

	# Document Processing Settings
	CHUNK_SIZE: int = Field(1000, description="Document chunk size")
	CHUNK_OVERLAP: int = Field(200, description="Document chunk overlap")
	MAX_HISTORY_LENGTH: int = Field(10, description="Maximum conversation history length")

	# Conversation Summarization Settings (from your chatbot)
	ENABLE_CONVERSATION_SUMMARIZATION: bool = Field(True, description="Enable conversation summarization")
	SUMMARIZATION_THRESHOLD: int = Field(16, description="Message pairs threshold for summarization")
	MAX_DETAILED_MESSAGES: int = Field(8, description="Maximum detailed messages to keep before summarization")
	CONTEXT_WINDOW_THRESHOLD: float = Field(0.7, description="Context window usage threshold for summarization")
	SUMMARIZATION_LLM_PROVIDER: str = Field("groq", description="LLM provider for summarization")
	SUMMARIZATION_LLM_MODEL: str = Field("llama-3.1-8b-instant", description="LLM model for summarization")

	# LLM API Keys
	OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
	GEMINI_API_KEY: Optional[str] = Field(None, description="Google Gemini API key")
	GROQ_API_KEY: Optional[str] = Field(None, description="Groq API key")
	DEEPSEEK_API_KEY: Optional[str] = Field(None, description="DeepSeek API key")

	# LLM Provider Selection
	LLM_PROVIDER: str = Field("groq", description="Active LLM provider (groq, deepseek, openai, gemini)")
	
	# LLM Default Settings (your chatbot defaults preserved)
	DEFAULT_LLM_PROVIDER: str = Field("groq", description="Default LLM provider")
	DEFAULT_LLM_MODEL: str = Field("llama-3.1-8b-instant", description="Default LLM model")
	DEFAULT_TEMPERATURE: float = Field(0.7, description="Default LLM temperature")
	DEFAULT_MAX_TOKENS: int = Field(4000, description="Default max tokens")
	
	# DeepSeek specific settings
	DEEPSEEK_MODEL: str = Field("deepseek-chat", description="DeepSeek model name")
	DEEPSEEK_TEMPERATURE: float = Field(0.7, description="DeepSeek temperature")
	DEEPSEEK_MAX_TOKENS: int = Field(4000, description="DeepSeek max tokens")

	# AI/ML Settings (friend's version for compatibility)
	MODEL_NAME: str = Field("gpt-3.5-turbo", description="Default model name (compatibility)")
	MAX_TOKENS: int = Field(2000, description="Maximum tokens (compatibility)")
	TEMPERATURE: float = Field(0.7, description="Model temperature (compatibility)")
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

	# MinIO Settings (friend's version)
	MINIO_ENDPOINT: str = Field("localhost:9000", description="MinIO endpoint")
	MINIO_ACCESS_KEY: str = Field("minioadmin", description="MinIO access key")
	MINIO_SECRET_KEY: str = Field("minioadmin", description="MinIO secret key")
	MINIO_BUCKET_NAME: str = Field("documents", description="MinIO bucket name")
	MINIO_SECURE: bool = Field(False, description="MinIO secure connection")

	@field_validator('CORS_ORIGINS', mode='before')
	@classmethod
	def parse_cors_origins(cls, v):
		if isinstance(v, str):
			try:
				return json.loads(v)  # JSON string
			except json.JSONDecodeError:
				return [origin.strip() for origin in v.split(',')]  # comma-separated
		return v

	@field_validator('DEBUG', mode='before')
	@classmethod
	def parse_debug(cls, v):
		if isinstance(v, str):
			return v.lower() in ('true', '1', 'yes', 'on')
		return v

	def get_database_url(self) -> str:
		"""Build a database URL from any available settings."""
		# Direct URLs first
		if self.DATABASE_URL:
			return self.DATABASE_URL
		if self.database_url:
			return self.database_url

		# Helper to pick first non-empty value
		def pick(*values, default=None):
			for value in values:
				if value not in (None, ""):
					return value
			return default

		# Coerce port to int-ish string
		def to_port_str(value, fallback: int) -> str:
			if value in (None, ""):
				return str(fallback)
			try:
				return str(int(value))
			except Exception:
				return str(fallback)

		host = pick(self.DATABASE_HOST, self.DB_HOST, self.db_host, default="localhost")
		port = to_port_str(pick(self.DATABASE_PORT, self.DB_PORT, self.db_port, default=5432), 5432)
		user = pick(self.DATABASE_USER, self.DB_USER, self.db_user, default="postgres")
		password = pick(self.DATABASE_PASSWORD, self.DB_PASSWORD, self.db_password, default="")
		name = pick(self.DATABASE_NAME, self.DB_NAME, self.db_name, default="docanalyzer")

		return f"postgresql://{user}:{password}@{host}:{port}/{name}"


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


# Create global settings instance from environment
settings = get_settings_by_env()

# Optional: print DB URL in debug mode
if settings.DEBUG:
	print(f"DB URL used by FastAPI: {settings.get_database_url()}")


def get_settings() -> Settings:
	"""
	Get the global settings instance.
	Returns:
		Settings: The global settings instance
	"""
	return settings


__all__ = ["settings", "get_settings", "get_settings_by_env", "Settings", "DevelopmentSettings", "ProductionSettings", "TestingSettings"]