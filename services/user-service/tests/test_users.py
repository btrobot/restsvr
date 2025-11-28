"""
用户管理端点测试
测试用户 CRUD 操作
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    """测试创建用户"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123",
        "full_name": "Test User"
    }

    response = await async_client.post("/api/users/", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_user_duplicate_username(async_client: AsyncClient):
    """测试创建重复用户名的用户"""
    user_data = {
        "username": "duplicate",
        "email": "duplicate1@example.com",
        "password": "SecurePass123"
    }

    # 第一次创建
    await async_client.post("/api/users/", json=user_data)

    # 第二次创建（相同的用户名）
    user_data["email"] = "duplicate2@example.com"
    response = await async_client.post("/api/users/", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "用户名已存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient):
    """测试创建重复邮箱的用户"""
    user_data = {
        "username": "test1",
        "email": "same@example.com",
        "password": "SecurePass123"
    }

    # 第一次创建
    await async_client.post("/api/users/", json=user_data)

    # 第二次创建（相同的邮箱）
    user_data["username"] = "test2"
    response = await async_client.post("/api/users/", json=user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "邮箱已注册" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_users(async_client: AsyncClient):
    """测试获取用户列表"""
    # 先创建几个用户
    users_data = [
        {"username": f"user{i}", "email": f"user{i}@example.com", "password": "pass123"}
        for i in range(3)
    ]

    for user_data in users_data:
        await async_client.post("/api/users/", json=user_data)

    # 获取用户列表
    response = await async_client.get("/api/users/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert len(data) >= 3
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient):
    """测试根据 ID 获取用户"""
    # 创建用户
    user_data = {
        "username": "getuser",
        "email": "get@example.com",
        "password": "SecurePass123"
    }

    create_response = await async_client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]

    # 获取用户
    response = await async_client.get(f"/api/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == user_id
    assert data["username"] == user_data["username"]


@pytest.mark.asyncio
async def test_get_nonexistent_user(async_client: AsyncClient):
    """测试获取不存在的用户"""
    response = await async_client.get("/api/users/99999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "用户不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user(async_client: AsyncClient):
    """测试更新用户信息"""
    # 创建用户
    user_data = {
        "username": "update_user",
        "email": "update@example.com",
        "password": "SecurePass123"
    }

    create_response = await async_client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]

    # 更新用户
    update_data = {
        "full_name": "Updated Name",
        "is_active": False
    }

    response = await async_client.put(f"/api/users/{user_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["full_name"] == update_data["full_name"]
    assert data["is_active"] == update_data["is_active"]


@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient):
    """测试删除用户（软删除）"""
    # 创建用户
    user_data = {
        "username": "delete_user",
        "email": "delete@example.com",
        "password": "SecurePass123"
    }

    create_response = await async_client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]

    # 删除用户
    delete_response = await async_client.delete(f"/api/users/{user_id}")

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # 验证用户已被删除（软删除，但标记为非活跃）
    get_response = await async_client.get(f"/api/users/{user_id}")
    user_data = get_response.json()
    assert user_data["is_active"] is False


@pytest.mark.asyncio
async def test_get_user_by_username(async_client: AsyncClient):
    """测试根据用户名查找用户"""
    # 创建用户
    user_data = {
        "username": "search_user",
        "email": "search@example.com",
        "password": "SecurePass123",
        "full_name": "Search User"
    }

    await async_client.post("/api/users/", json=user_data)

    # 搜索用户
    response = await async_client.get(f"/api/users/search/by-username/{user_data['username']}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_activate_deactivate_user(async_client: AsyncClient):
    """测试激活和禁用用户"""
    # 创建用户（默认激活）
    user_data = {
        "username": "activate_test",
        "email": "activate@example.com",
        "password": "SecurePass123"
    }

    create_response = await async_client.post("/api/users/", json=user_data)
    user_id = create_response.json()["id"]

    # 禁用用户
    deactivate_response = await async_client.post(f"/api/users/{user_id}/deactivate")
    assert deactivate_response.status_code == status.HTTP_200_OK

    user_data = deactivate_response.json()
    assert user_data["is_active"] is False

    # 激活用户
    activate_response = await async_client.post(f"/api/users/{user_id}/activate")
    assert activate_response.status_code == status.HTTP_200_OK

    user_data = activate_response.json()
    assert user_data["is_active"] is True
