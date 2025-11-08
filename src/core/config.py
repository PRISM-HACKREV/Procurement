"""
Configuration management for PRISMA Procurement API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Mock Mode
    USE_MOCK: bool = True
    SOURCE_MODE: str = "sandbox"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "PRISMA Procurement API"
    API_VERSION: str = "1.0.0"
    
    # Simulation Settings
    MIN_LATENCY_MS: int = 200
    MAX_LATENCY_MS: int = 600
    CACHE_TTL_HOURS: int = 24
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_STATUS_CODE: int = 429
    
    # Price Jitter (percentage)
    PRICE_JITTER_MIN: float = 0.99
    PRICE_JITTER_MAX: float = 1.02
    
    # Default coordinates for Hyderabad
    DEFAULT_LATITUDE: float = 17.3850
    DEFAULT_LONGITUDE: float = 78.4867
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

