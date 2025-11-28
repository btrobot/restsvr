"""
用户管理路由
提供用户 CRUD 操作的 API
"""
from http.client import HTTPException
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
import redis.asyncio as redis
import bcrypt

from ..core.database import get_db
from ..core.config import settings
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()


def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建新用户账户"
)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """创建新用户"""
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已注册"
        )

    # 创建用户实例
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
        is_active=user.is_active if user.is_active is not None else True
    )

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="创建用户失败，请检查输入数据"
        )


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="获取用户列表",
    description="获取所有用户列表（分页功能可扩展）"
)
async def get_users(db: AsyncSession = Depends(get_db)):
    """获取所有用户"""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="获取用户详情",
    description="根据用户ID获取用户详细信息"
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="更新用户信息",
    description="更新用户的邮箱、姓名等信息（密码需单独接口）"
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = func.now()

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新失败，请检查输入数据"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    description="软删除用户（将 is_active 设为 false）"
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """删除用户（软删除）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 软删除
    user.is_active = False
    await db.commit()

    return None


@router.get(
    "/search/by-username/{username}",
    response_model=UserResponse,
    summary="根据用户名查找用户",
    description="根据用户名精确查找用户"
)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """根据用户名查找用户"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户 {username} 不存在"
        )

    return user


@router.post("/{user_id}/activate", response_model=UserResponse, summary="激活用户")
async def activate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """激活用户账户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse, summary="禁用用户")
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """禁用用户账户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user
