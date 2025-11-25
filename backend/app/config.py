"""
Centralized configuration for backend services using Pydantic BaseSettings.
Loads environment variables with validation and default values.
"""
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class BackendConfig(BaseSettings):
    """Backend configuration with environment variable loading"""
    
    # API Server Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")
    OPENAI_BASE_URL: Optional[str] = Field(default=None, description="OpenAI API base URL")
    
    # Database Configuration
    DB_URL: Optional[str] = Field(default=None, description="PostgreSQL database URL")
    
    # Redis Configuration
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # Qdrant Vector DB Configuration
    QDRANT_URL: Optional[str] = Field(default="http://localhost:6333", description="Qdrant server URL")
    
    # Neo4j Graph DB Configuration
    NEO4J_URI: Optional[str] = Field(default=None, description="Neo4j connection URI")
    NEO4J_AUTH: Optional[str] = Field(default=None, description="Neo4j auth (user/password)")
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, description="Telegram bot token")
    TELEGRAM_ALLOWLIST: Optional[str] = Field(default=None, description="Comma-separated Telegram user IDs")
    ENABLE_TELEGRAM_FORWARD: bool = Field(default=False, description="Enable Telegram forwarding")
    
    # GitHub Configuration
    GITHUB_REPO: Optional[str] = Field(default=None, description="GitHub repository")
    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub access token")
    
    # Ingestion Configuration
    CIRCULARS_INDEX: str = Field(
        default="data/sama_regulations/sama_circulars.index.jsonl",
        description="Path to JSONL index file"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global config instance
config = BackendConfig()


def get_config() -> BackendConfig:
    """Get the global configuration instance"""
    return config
