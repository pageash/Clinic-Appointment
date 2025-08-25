"""
Application configuration settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Clinic Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str
    DATABASE_URL_TEST: Optional[str] = None
    
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads/"
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v):
        if isinstance(v, str):
            return v
        return f"postgresql://{v.get('user')}:{v.get('password')}@{v.get('host')}:{v.get('port')}/{v.get('database')}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Create settings instance
settings = Settings()


# Database configuration for different environments
def get_database_url(test: bool = False) -> str:
    """Get database URL for current environment"""
    if test and settings.DATABASE_URL_TEST:
        return settings.DATABASE_URL_TEST
    return settings.DATABASE_URL


# Logging configuration
def get_log_config():
    """Get logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default"],
        },
    }
