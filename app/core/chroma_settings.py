import os
from pathlib import Path

# This class defines global configuration settings for Chroma DB.
class Settings:
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME = "documents"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5