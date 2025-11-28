"""
健康检查端点测试
测试 /health 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """测试健康检查端点"""
    response = await async_client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"
    assert "database" in data
    assert "service" in data


@pytest.mark.asyncio
async def test_readiness_check(async_client: AsyncClient):
    """测试就绪检查端点"""
    response = await async_client.get("/health/ready")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "status" in data
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_liveness_check(async_client: AsyncClient):
    """测试存活检查端点"""
    response = await async_client.get("/health/live")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "status" in data
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_detailed_health_check(async_client: AsyncClient):
    """测试详细健康检查端点"""
    response = await async_client.get("/health/details")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "service" in data
    assert "database" in data
    assert "system" in data

    # 检查 service 部分
    assert data["service"]["status"] == "ok"
    assert "timestamp" in data["service"]

    # 检查 database 部分
    assert data["database"]["status"] == "ok"
    assert "response_time" in data["database"]

    # 检查 system 部分
    assert "platform" in data["system"]
    assert "python_version" in data["system"]
