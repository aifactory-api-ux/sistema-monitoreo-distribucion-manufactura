import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from functools import lru_cache

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./distroviz.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Server Configuration
    backend_host: str = Field(
        default="0.0.0.0",
        env="BACKEND_HOST",
        description="Backend server host"
    )
    
    backend_port: int = Field(
        default=8000,
        env="BACKEND_PORT",
        description="Backend server port"
    )
    
    frontend_port: int = Field(
        default=3000,
        env="FRONTEND_PORT",
        description="Frontend server port"
    )
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://frontend:3000"
        ],
        env="CORS_ORIGINS",
        description="Allowed CORS origins"
    )
    
    cors_credentials: bool = Field(
        default=True,
        env="CORS_CREDENTIALS",
        description="Allow CORS credentials"
    )
    
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_METHODS",
        description="Allowed CORS methods"
    )
    
    cors_headers: List[str] = Field(
        default=["*"],
        env="CORS_HEADERS",
        description="Allowed CORS headers"
    )
    
    # Application Configuration
    app_name: str = Field(
        default="DistroViz v3",
        env="APP_NAME",
        description="Application name"
    )
    
    app_version: str = Field(
        default="3.0.0",
        env="APP_VERSION",
        description="Application version"
    )
    
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # Database Pool Configuration
    db_pool_size: int = Field(
        default=10,
        env="DB_POOL_SIZE",
        description="Database connection pool size"
    )
    
    db_max_overflow: int = Field(
        default=20,
        env="DB_MAX_OVERFLOW",
        description="Database connection pool max overflow"
    )
    
    db_pool_timeout: int = Field(
        default=30,
        env="DB_POOL_TIMEOUT",
        description="Database connection pool timeout in seconds"
    )
    
    db_pool_recycle: int = Field(
        default=3600,
        env="DB_POOL_RECYCLE",
        description="Database connection pool recycle time in seconds"
    )
    
    # API Configuration
    api_prefix: str = Field(
        default="/api",
        env="API_PREFIX",
        description="API route prefix"
    )
    
    docs_url: Optional[str] = Field(
        default="/docs",
        env="DOCS_URL",
        description="API documentation URL (set to None to disable)"
    )
    
    redoc_url: Optional[str] = Field(
        default="/redoc",
        env="REDOC_URL",
        description="ReDoc documentation URL (set to None to disable)"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Logging format"
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @field_validator('cors_methods', mode='before')
    @classmethod
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip().upper() for method in v.split(',')]
        return v

    @field_validator('cors_headers', mode='before')
    @classmethod
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(',')]
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        if not v:
            raise ValueError('DATABASE_URL is required')
        if not v.startswith(('sqlite:///', 'postgresql://', 'mysql://')):
            raise ValueError('DATABASE_URL must start with sqlite:///, postgresql://, or mysql://')
        return v
    
    @property
    def is_sqlite(self) -> bool:
        """Check if the database is SQLite"""
        return self.database_url.startswith('sqlite')
    
    @property
    def is_postgresql(self) -> bool:
        """Check if the database is PostgreSQL"""
        return self.database_url.startswith('postgresql')
    
    @property
    def is_mysql(self) -> bool:
        """Check if the database is MySQL"""
        return self.database_url.startswith('mysql')
    
    @property
    def database_file_path(self) -> Optional[str]:
        """Get the SQLite database file path if using SQLite"""
        if self.is_sqlite:
            return self.database_url.replace('sqlite:///', '')
        return None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    try:
        settings = Settings()
        
        # Validate required environment variables
        if not settings.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Create database directory if using SQLite
        if settings.is_sqlite and settings.database_file_path:
            db_dir = os.path.dirname(settings.database_file_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        return settings
    
    except Exception as e:
        print(f"Configuration error: {e}")
        print("Please check your environment variables and .env file")
        raise

def validate_environment() -> None:
    """Validate all required environment variables at startup"""
    try:
        settings = get_settings()
        
        # Check database connectivity requirements
        if settings.is_sqlite:
            db_path = settings.database_file_path
            if db_path:
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.access(db_dir, os.W_OK):
                    raise PermissionError(f"No write permission for database directory: {db_dir}")
        
        print(f"Configuration validated successfully:")
        print(f"  App: {settings.app_name} v{settings.app_version}")
        print(f"  Database: {settings.database_url}")
        print(f"  Backend: {settings.backend_host}:{settings.backend_port}")
        print(f"  CORS Origins: {settings.cors_origins}")
        print(f"  Debug Mode: {settings.debug}")
        
    except Exception as e:
        print(f"Environment validation failed: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    validate_environment()