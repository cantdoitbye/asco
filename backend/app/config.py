import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Ooumph SHAKTI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:password@localhost:5432/ooumph_shakti"
    )
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
