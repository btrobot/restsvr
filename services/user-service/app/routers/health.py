"""
健康检查路由
提供服务健康状态检查
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
import redis.asyncio as redis
import asyncio

router = APIRouter()


@router.get("/health", summary="健康检查", description="检查服务、数据库和 Redis 的健康状态")
async def health_check(db: AsyncSession = Depends(get_db)):
    """健康检查端点"""
    checks = {
        "service": "ok",
        "database": "unknown",
        "redis": "unknown"
    }

    # 检查数据库连接
    try:
        result = await db.execute(text("SELECT 1"))
        await db.scalar(result)
        checks["database"] = "ok"
    except SQLAlchemyError as e:
        checks["database"] = f"error: {str(e)}"

    # 检查 Redis 连接
    try:
        # 这里应该使用 app.state.redis
        checks["redis"] = "unknown"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    # 判断整体健康状态
    if checks["database"] == "ok":
        return {"status": "healthy", **checks}
    else:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", **checks}
        )


@router.get("/health/ready", summary="就绪检查", description="检查服务是否已准备好接收流量")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """就绪检查端点"""
    try:
        # 检查数据库
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "reason": "database not available"}
        )


@router.get("/health/live", summary="存活检查", description="检查服务是否存活")
async def liveness_check():
    """存活检查端点"""
    return {"status": "alive"}


@router.get("/health/details", summary="详细健康检查", description="提供详细的系统信息")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """详细健康检查端点"""
    import platform
    import psutil
    import time

    checks = {
        "service": {
            "status": "ok",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": time.time(),
        },
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_percent": psutil.virtual_memory().percent,
        },
        "database": {
            "status": "unknown"
        },
        "redis": {
            "status": "unknown"
        }
    }

    # 数据库检查
    try:
        start_time = time.time()
        await db.execute(text("SELECT 1"))
        db_time = (time.time() - start_time) * 1000
        checks["database"] = {
            "status": "ok",
            "response_time": f"{db_time:.2f}ms"
        }
    except SQLAlchemyError as e:
        checks["database"] = {
            "status": "error",
            "error": str(e)
        }

    return checks
