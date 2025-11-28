"""
Pytest 配置和共享固件
提供测试所需的公共组件
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine, get_db, Base
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from app.main import app


# 测试数据库 URL（使用内存 SQLite 进行测试）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """
    创建事件循环
    使 async fixtures 能够正确工作
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    设置测试数据库
    在所有测试开始前创建表结构
    """
    # 连接测试数据库
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    yield

    # 测试结束后清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncSession:
    """
    数据库会话固件
    每个测试用例使用独立的事务，测试后自动回滚
    """
    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    # 清理
    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def async_client():
    """
    HTTP 客户端固件
    用于测试 API 端点
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
