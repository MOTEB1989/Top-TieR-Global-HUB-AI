"""
Configuration settings using Pydantic
إعدادات التكوين باستخدام Pydantic
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    إعدادات التطبيق المحملة من متغيرات البيئة
    """
    # Environment
    ENV: str = "development"
    
    # Database
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Security
    JWT_SECRET: Optional[str] = None
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    ADMIN_CHAT_ID: Optional[str] = None
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
