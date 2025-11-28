"""
配置管理模块
从环境变量加载应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""

    # 项目基础配置
    PROJECT_NAME: str = "FastAPI 微服务"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # 服务配置
    SERVICE_NAME: Optional[str] = "user-service"
    SERVICE_PORT: Optional[int] = 8000

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./test.db"

    # PostgreSQL 配置
    POSTGRES_DB: str = "microservices"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # MySQL 配置
    MYSQL_DATABASE: str = "microservices"
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_ROOT_PASSWORD: str = "root"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or plain

    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS 配置
    ALLOWED_ORIGINS: str = "*"

    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 100

    # API 文档
    ENABLE_DOCS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
