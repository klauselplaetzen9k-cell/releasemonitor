from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mariadb+pymysql://releasemonitor:password@mariadb:3306/releasemonitor"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (SMTP) - System-wide configuration
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "releases@example.com"
    
    # GitHub Token
    GITHUB_TOKEN: Optional[str] = None
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost"]
    
    # AI Summarization (optional)
    AI_ENABLED: bool = False
    AI_PROVIDER: str = "openai"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
