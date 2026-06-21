from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Campus Study Assistant"
    DEBUG: bool = False
    
    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str = "campus_study_assistant"
    
    # Qdrant Cloud
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "study_documents"
    QDRANT_VECTOR_SIZE: int = 384  # FastEmbed BGE-small produces 384-dim embeddings
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Groq (Fast LLM API)
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    # Available models:
    # llama-3.1-70b-versatile - Most versatile, great for all tasks
    # llama-3.1-8b-instant - Fastest, good for simple tasks
    # mixtral-8x7b-32768 - Balanced speed and quality
    # gemma2-9b-it - Google's efficient model
    
    # PDF Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # RAG
    TOP_K_RETRIEVAL: int = 10  # Increased from 5 to 10 for more context
    SIMILARITY_THRESHOLD: float = 0.0  # No threshold - rely on TOP_K and LLM filtering instead
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
