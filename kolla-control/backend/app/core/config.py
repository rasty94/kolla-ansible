"""
Application configuration using Pydantic Settings
"""
from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "Kolla-Control"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Celery
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Kolla-Ansible
    KOLLA_ANSIBLE_PATH: str = "/usr/local/share/kolla-ansible"
    KOLLA_CONFIG_PATH: str = "/etc/kolla"
    ANSIBLE_INVENTORY_PATH: str = "/etc/kolla/inventory"
    
    # Foreman Integration
    FOREMAN_ENABLED: bool = False
    FOREMAN_URL: Optional[str] = None
    FOREMAN_API_USER: Optional[str] = None
    FOREMAN_API_PASSWORD: Optional[str] = None
    FOREMAN_VERIFY_SSL: bool = True
    
    # Prometheus Integration
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_URL: str = "http://localhost:9090"
    
    # Grafana Integration
    GRAFANA_ENABLED: bool = True
    GRAFANA_URL: str = "http://localhost:3000"
    GRAFANA_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9091


# Create settings instance
settings = Settings()
