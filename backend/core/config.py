from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    ENVIRONMENT: str = "development"
    APP_NAME: str = "HealthGuard AI Backend"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://healthguard:healthguard_dev_password@localhost:5432/healthguard"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kafka
    KAFKA_BROKERS: str = "localhost:9093"
    
    # MCP Server
    MCP_SERVER_URL: str = "http://localhost:3000"
    
    # Security
    JWT_SECRET: str = "dev_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 15
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3001"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
