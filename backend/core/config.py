from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import List
import json
import os

class Settings(BaseSettings):
    # Only use .env for simple string values, not for complex types
    model_config = ConfigDict(case_sensitive=True)
    
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_NAME: str = os.getenv("APP_NAME", "HealthGuard AI Backend")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://healthguard:healthguard_dev_password@localhost:5432/healthguard")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Kafka
    KAFKA_BROKERS: str = os.getenv("KAFKA_BROKERS", "localhost:9093")
    
    # MCP Server
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev_secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "15"))
    
    # CORS - These have sensible defaults
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3001", "http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]

settings = Settings()
