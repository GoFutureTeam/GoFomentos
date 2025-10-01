"""
Settings for the application
"""
import os
from typing import Optional, Dict, Any
from pydantic import validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Settings(BaseSettings):
    # API
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Editais API")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://admin:password@mongo:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "editais_db")
    MONGO_USER: Optional[str] = os.getenv("MONGO_USER")
    MONGO_PASSWORD: Optional[str] = os.getenv("MONGO_PASSWORD")
    
    # ChromaDB
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "chroma")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", 8001))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "editais")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Jina AI
    JINA_API_KEY: str = os.getenv("JINA_API_KEY", "")
    
    # PDF Processing
    PDF_CHUNK_SIZE: int = int(os.getenv("PDF_CHUNK_SIZE", 1000))
    UUID_NAMESPACE_EDITAIS: str = os.getenv("UUID_NAMESPACE_EDITAIS", "5aa0b3b9-9a85-4f5f-8c28-6f4f2c4b2a10")
    TIMEZONE: str = os.getenv("TIMEZONE", "America/Fortaleza")
    
    @validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v
    
    @validator("JINA_API_KEY")
    def validate_jina_api_key(cls, v):
        if not v:
            raise ValueError("JINA_API_KEY is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
