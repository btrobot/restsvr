"""
用户数据模式（Schema）
使用 Pydantic 进行数据验证和序列化
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名，3-50个字符")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名，可选")
    is_active: Optional[bool] = Field(True, description="是否激活")
    is_superuser: Optional[bool] = Field(False, description="是否为超级用户")

    @validator('username')
    def username_alphanumeric(cls, v):
        """验证用户名是否为字母数字组合"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @validator('full_name')
    def full_name_optional(cls, v):
        """全名可以为空"""
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False
            }
        }


class UserCreate(UserBase):
    """创建用户请求模式"""
    password: str = Field(..., min_length=6, max_length=128, description="密码，6-128个字符")

    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少为6个字符')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "jane_doe",
                "email": "jane@example.com",
                "password": "SecurePass123",
                "full_name": "Jane Doe"
            }
        }


class UserUpdate(BaseModel):
    """更新用户请求模式"""
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_superuser: Optional[bool] = Field(None, description="是否为超级用户")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Smith",
                "is_active": True
            }
        }


class UserResponse(UserBase):
    """用户响应模式"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }


class UserInDB(UserBase):
    """数据库用户模式（包含密码哈希）"""
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token 响应模式"""
    access_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    """Token 载荷模式"""
    sub: Optional[int] = None
    exp: Optional[int] = None


class UserLogin(BaseModel):
    """用户登录请求模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名或邮箱")
    password: str = Field(..., min_length=6, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "SecurePass123"
            }
        }
