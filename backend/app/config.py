"""Configuration settings for the application"""
import json
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = Field(
        default="postgresql://udds:udds_password@localhost:5432/udds",
        description="PostgreSQL connection URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Google Sheets
    google_sheets_credentials: Optional[str] = Field(
        default=None,
        description="Google Sheets service account credentials JSON"
    )
    
    # Security
    webhook_secret: str = Field(
        default="dev-secret-change-in-production",
        description="Secret for webhook signature validation"
    )
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8088"],
        description="Allowed CORS origins"
    )
    
    # Application
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # API
    api_v1_str: str = Field(
        default="/api/v1",
        description="API version 1 prefix"
    )
    
    # Sync
    default_sync_interval_minutes: int = Field(
        default=60,
        description="Default sync interval in minutes"
    )
    
    # File paths
    datasets_config_path: str = Field(
        default="/app/config/datasets.json",
        description="Path to datasets configuration file"
    )
    reports_config_path: str = Field(
        default="/app/config/reports.json",
        description="Path to reports configuration file"
    )
    
    @validator('google_sheets_credentials', pre=True)
    def parse_google_credentials(cls, v):
        """Parse Google Sheets credentials from JSON string"""
        if v and isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If it's already a dict or invalid, return as is
                return v
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()