"""
数据库配置模块
支持 SQLite、PostgreSQL 和 MySQL
自动根据 DATABASE_URL 选择正确的数据库驱动
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建基础模型类
Base = declarative_base()
metadata = MetaData()


def create_engine():
    """
    创建异步数据库引擎
    根据环境自动选择正确的数据库驱动
    """
    database_url = settings.DATABASE_URL

    # 数据库驱动映射
    driver_mapping = {
        "sqlite": {
            "sync": "sqlite:///./test.db",
            "async": "sqlite+aiosqlite:///./test.db",
        },
        "postgresql": {
            "sync": f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
            "async": f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
        },
        "mysql": {
            "sync": f"mysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
            "async": f"mysql+asyncmy://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
        },
    }

    # 自动检测数据库类型并选择正确的驱动
    if database_url.startswith("sqlite"):
        db_type = "sqlite"
        final_url = driver_mapping["sqlite"]["async"]
    elif database_url.startswith("postgresql") or settings.POSTGRES_HOST != "localhost":
        db_type = "postgresql"
        final_url = driver_mapping["postgresql"]["async"]
    elif database_url.startswith("mysql") or settings.MYSQL_HOST != "localhost":
        db_type = "mysql"
        final_url = driver_mapping["mysql"]["async"]
    else:
        # 默认使用 SQLite
        db_type = "sqlite"
        final_url = driver_mapping["sqlite"]["async"]

    logger.info(f"使用 {db_type.upper()} 数据库: {final_url.split('://')[0]}")

    # SQLite 特殊配置
    if db_type == "sqlite":
        connect_args = {"check_same_thread": False}
        return create_async_engine(
            final_url,
            echo=settings.ENVIRONMENT == "development",  # 开发环境显示 SQL
            connect_args=connect_args,
        )
    else:
        # PostgreSQL 或 MySQL 配置
        pool_size = settings.POSTGRES_POOL_SIZE if db_type == "postgresql" else 20
        max_overflow = settings.POSTGRES_MAX_OVERFLOW if db_type == "postgresql" else 10

        return create_async_engine(
            final_url,
            echo=settings.ENVIRONMENT == "development",
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # 预检测连接是否可用
        )


# 创建异步引擎
engine = create_engine()

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    获取数据库会话
    依赖注入使用，自动关闭会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    创建数据库表（用于初始化）
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")


async def drop_tables():
    """
    删除数据库表（用于测试）
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("数据库表删除完成")
