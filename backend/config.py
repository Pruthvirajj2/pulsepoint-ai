"""Configuration management for PulsePoint AI"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    assemblyai_api_key: str = ""
    google_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Processing
    max_clips: int = 5
    min_clip_duration: int = 15
    max_clip_duration: int = 60
    target_aspect_ratio: str = "9:16"

    # Paths
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    temp_dir: Path = Path("temp")

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


def ensure_directories():
    """Create necessary directories"""
    settings = get_settings()
    settings.upload_dir.mkdir(exist_ok=True)
    settings.output_dir.mkdir(exist_ok=True)
    settings.temp_dir.mkdir(exist_ok=True)
