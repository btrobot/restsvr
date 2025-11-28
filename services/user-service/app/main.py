"""
用户服务 - 主应用文件
提供用户注册、登录、信息管理等 API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
import redis.asyncio as redis
import os

from .core.database import engine, Base, get_db
from .core.config import settings
from .routers import health, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时创建数据库表和 Redis 连接
    关闭时释放资源
    """
    print("🚀 用户服务正在启动...")

    # 创建数据库表（如果不存在）
    print("📦 初始化数据库...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 连接 Redis
    print("🔄 连接 Redis...")
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        encoding="utf-8"
    )

    try:
        await redis_client.ping()
        app.state.redis = redis_client
        print("✅ Redis 连接成功")
    except Exception as e:
        print(f"⚠️ Redis 连接失败: {e}")
        app.state.redis = None

    print("✅ 用户服务启动完成！")

    yield

    # 关闭 Redis 连接
    if app.state.redis:
        await app.state.redis.close()
        print("🔄 Redis 连接已关闭")

    print("👋 用户服务已停止")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title="用户服务 API",
        description="提供用户注册、登录、信息管理等功能的微服务",
        version="1.0.0",
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_DOCS else None,
        openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
        lifespan=lifespan
    )

    # CORS 配置
    if settings.ALLOWED_ORIGINS:
        origins = settings.ALLOWED_ORIGINS.split(",")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 注册路由
    app.include_router(health.router)
    app.include_router(users.router, prefix="/api/users", tags=["users"])

    return app


app = create_app()


@app.get("/")
async def root():
    """服务根路径"""
    return {
        "service": settings.SERVICE_NAME or "user-service",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENABLE_DOCS else None,
        "health": "/health"
    }


if __name__ == "__main__":
    # 从环境变量读取运行配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") == "development"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )
