"""
Production Configuration Manager
Loads config based on deployment platform and environment
"""
import os
from typing import Dict, Any, Optional
from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field


class DeploymentPlatform(str, Enum):
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class LLMMode(str, Enum):
    LOCAL = "local"
    API = "api"
    HYBRID = "hybrid"


class ProductionSettings(BaseSettings):
    """Production-ready configuration with platform detection"""
    
    # ============ DEPLOYMENT ============
    deployment_platform: DeploymentPlatform = Field(
        default=DeploymentPlatform.LOCAL,
        env="DEPLOYMENT_PLATFORM"
    )
    environment: str = Field(default="production", env="ENVIRONMENT")
    app_name: str = Field(default="healthguard-ai", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    
    # ============ APPLICATION ============
    backend_port: int = Field(default=8000, env="BACKEND_PORT")
    backend_host: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    backend_workers: int = Field(default=4, env="BACKEND_WORKERS")
    
    mcp_port: int = Field(default=3000, env="MCP_PORT")
    mcp_host: str = Field(default="0.0.0.0", env="MCP_HOST")
    
    # ============ LLM CONFIGURATION ============
    llm_mode: LLMMode = Field(default=LLMMode.LOCAL, env="LLM_MODE")
    
    # Local LLM
    local_llm_enabled: bool = Field(default=True, env="LOCAL_LLM_ENABLED")
    local_llm_provider: str = Field(default="ollama", env="LOCAL_LLM_PROVIDER")
    local_llm_host: str = Field(default="http://localhost:11434", env="LOCAL_LLM_HOST")
    local_llm_model: str = Field(default="llama3.2:latest", env="LOCAL_LLM_MODEL")
    local_llm_context_length: int = Field(default=8192, env="LOCAL_LLM_CONTEXT_LENGTH")
    local_llm_temperature: float = Field(default=0.7, env="LOCAL_LLM_TEMPERATURE")
    
    # API LLM
    api_llm_enabled: bool = Field(default=False, env="API_LLM_ENABLED")
    api_llm_provider: str = Field(default="openai", env="API_LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # Azure OpenAI
    azure_openai_enabled: bool = Field(default=False, env="AZURE_OPENAI_ENABLED")
    azure_openai_key: Optional[str] = Field(default=None, env="AZURE_OPENAI_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    
    # ============ DATABASE ============
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="healthguard", env="DATABASE_NAME")
    database_user: str = Field(default="healthguard_user", env="DATABASE_USER")
    database_password: str = Field(default="", env="DATABASE_PASSWORD")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_ssl_enabled: bool = Field(default=True, env="DATABASE_SSL_ENABLED")
    
    # AWS RDS
    aws_rds_enabled: bool = Field(default=False, env="AWS_RDS_ENABLED")
    aws_rds_endpoint: Optional[str] = Field(default=None, env="AWS_RDS_ENDPOINT")
    aws_rds_secret_arn: Optional[str] = Field(default=None, env="AWS_RDS_SECRET_ARN")
    
    # Azure PostgreSQL
    azure_postgres_enabled: bool = Field(default=False, env="AZURE_POSTGRES_ENABLED")
    azure_postgres_host: Optional[str] = Field(default=None, env="AZURE_POSTGRES_HOST")
    
    # GCP Cloud SQL
    gcp_cloudsql_enabled: bool = Field(default=False, env="GCP_CLOUDSQL_ENABLED")
    gcp_cloudsql_connection_name: Optional[str] = Field(default=None, env="GCP_CLOUDSQL_CONNECTION_NAME")
    
    # ============ CACHE ============
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # ============ MESSAGE QUEUE ============
    kafka_enabled: bool = Field(default=True, env="KAFKA_ENABLED")
    kafka_brokers: str = Field(default="localhost:9092", env="KAFKA_BROKERS")
    
    # ============ SECURITY ============
    jwt_secret: str = Field(default="change_me", env="JWT_SECRET")
    jwt_expiration: str = Field(default="24h", env="JWT_EXPIRATION")
    encryption_key: str = Field(default="change_me", env="ENCRYPTION_KEY")
    
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    allowed_hosts: str = Field(default="*", env="ALLOWED_HOSTS")
    
    # ============ AWS ============
    aws_enabled: bool = Field(default=False, env="AWS_ENABLED")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    aws_cloudwatch_enabled: bool = Field(default=True, env="AWS_CLOUDWATCH_ENABLED")
    
    # ============ AZURE ============
    azure_enabled: bool = Field(default=False, env="AZURE_ENABLED")
    azure_subscription_id: Optional[str] = Field(default=None, env="AZURE_SUBSCRIPTION_ID")
    azure_tenant_id: Optional[str] = Field(default=None, env="AZURE_TENANT_ID")
    azure_client_id: Optional[str] = Field(default=None, env="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(default=None, env="AZURE_CLIENT_SECRET")
    azure_storage_account: Optional[str] = Field(default=None, env="AZURE_STORAGE_ACCOUNT")
    azure_keyvault_enabled: bool = Field(default=False, env="AZURE_KEYVAULT_ENABLED")
    
    # ============ GCP ============
    gcp_enabled: bool = Field(default=False, env="GCP_ENABLED")
    gcp_project_id: Optional[str] = Field(default=None, env="GCP_PROJECT_ID")
    gcp_region: str = Field(default="us-central1", env="GCP_REGION")
    gcp_service_account_key_path: Optional[str] = Field(default=None, env="GCP_SERVICE_ACCOUNT_KEY_PATH")
    gcp_storage_bucket: Optional[str] = Field(default=None, env="GCP_STORAGE_BUCKET")
    
    # ============ MONITORING ============
    log_level: str = Field(default="info", env="LOG_LEVEL")
    sentry_enabled: bool = Field(default=False, env="SENTRY_ENABLED")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    datadog_enabled: bool = Field(default=False, env="DATADOG_ENABLED")
    datadog_api_key: Optional[str] = Field(default=None, env="DATADOG_API_KEY")
    
    # ============ FEATURES ============
    feature_ai_agents: bool = Field(default=True, env="FEATURE_AI_AGENTS")
    feature_predictive_analytics: bool = Field(default=True, env="FEATURE_PREDICTIVE_ANALYTICS")
    auto_scaling_enabled: bool = Field(default=False, env="AUTO_SCALING_ENABLED")
    
    # ============ COMPLIANCE ============
    hipaa_compliance_enabled: bool = Field(default=True, env="HIPAA_COMPLIANCE_ENABLED")
    gdpr_compliance_enabled: bool = Field(default=True, env="GDPR_COMPLIANCE_ENABLED")
    audit_logging_enabled: bool = Field(default=True, env="AUDIT_LOGGING_ENABLED")
    data_encryption_at_rest: bool = Field(default=True, env="DATA_ENCRYPTION_AT_REST")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def get_database_url(self) -> str:
        """Get database URL based on platform"""
        if self.deployment_platform == DeploymentPlatform.AWS and self.aws_rds_enabled:
            return self._get_aws_rds_url()
        elif self.deployment_platform == DeploymentPlatform.AZURE and self.azure_postgres_enabled:
            return self._get_azure_postgres_url()
        elif self.deployment_platform == DeploymentPlatform.GCP and self.gcp_cloudsql_enabled:
            return self._get_gcp_cloudsql_url()
        else:
            return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    def _get_aws_rds_url(self) -> str:
        """Get AWS RDS connection string"""
        if self.aws_rds_endpoint:
            return f"postgresql://{self.database_user}:{self.database_password}@{self.aws_rds_endpoint}:5432/{self.database_name}"
        return self.get_database_url()
    
    def _get_azure_postgres_url(self) -> str:
        """Get Azure PostgreSQL connection string"""
        if self.azure_postgres_host:
            return f"postgresql://{self.database_user}@{self.azure_postgres_host}:{self.database_password}@{self.azure_postgres_host}:5432/{self.database_name}?sslmode=require"
        return self.get_database_url()
    
    def _get_gcp_cloudsql_url(self) -> str:
        """Get GCP Cloud SQL connection string"""
        if self.gcp_cloudsql_connection_name:
            return f"postgresql://{self.database_user}:{self.database_password}@/{self.database_name}?host=/cloudsql/{self.gcp_cloudsql_connection_name}"
        return self.get_database_url()
    
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration based on mode"""
        config = {
            "mode": self.llm_mode,
            "local": None,
            "api": None
        }
        
        if self.llm_mode in [LLMMode.LOCAL, LLMMode.HYBRID]:
            config["local"] = {
                "enabled": self.local_llm_enabled,
                "provider": self.local_llm_provider,
                "host": self.local_llm_host,
                "model": self.local_llm_model,
                "context_length": self.local_llm_context_length,
                "temperature": self.local_llm_temperature
            }
        
        if self.llm_mode in [LLMMode.API, LLMMode.HYBRID]:
            config["api"] = {
                "enabled": self.api_llm_enabled,
                "provider": self.api_llm_provider,
                "openai": {
                    "api_key": self.openai_api_key,
                    "model": self.openai_model
                },
                "anthropic": {
                    "api_key": self.anthropic_api_key,
                    "model": self.anthropic_model
                },
                "azure_openai": {
                    "enabled": self.azure_openai_enabled,
                    "key": self.azure_openai_key,
                    "endpoint": self.azure_openai_endpoint
                }
            }
        
        return config
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def validate_production_config(self) -> list[str]:
        """Validate production configuration and return warnings"""
        warnings = []
        
        if self.is_production():
            if self.jwt_secret == "change_me":
                warnings.append("JWT_SECRET not set - SECURITY RISK!")
            if self.encryption_key == "change_me":
                warnings.append("ENCRYPTION_KEY not set - SECURITY RISK!")
            if not self.database_ssl_enabled:
                warnings.append("Database SSL disabled - not recommended for production")
            if not self.data_encryption_at_rest:
                warnings.append("Data encryption at rest disabled")
            if self.allowed_origins == "*":
                warnings.append("CORS allows all origins - SECURITY RISK!")
        
        return warnings


# Global settings instance
settings = ProductionSettings()
