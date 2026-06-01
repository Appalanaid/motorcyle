"""
Configuration management for the Motorcycle Recommendation API.
Loads environment variables from .env file.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings and configuration.
    Reads from environment variables and .env file.
    """

    # Database Configuration
    db_server: str = os.getenv("DB_SERVER", "localhost")
    db_database: str = os.getenv("DB_DATABASE", "Bike_DB")
    db_user: str = os.getenv("DB_USER", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "")
    use_windows_auth: bool = os.getenv("USE_WINDOWS_AUTH", "False").lower() == "true"

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model_vision: str = "gpt-4-vision-preview"
    openai_model_image: str = "dall-e-3"

    # Application Configuration
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Image Storage
    image_upload_dir: str = "./uploads"
    max_upload_size: int = 10485760  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
