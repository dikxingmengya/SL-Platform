"""
认证相关 Pydantic 模型
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str = Field(..., description="JWT 访问令牌")
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    role: str = Field(..., description="角色")
    is_super_admin: bool = Field(default=False, description="是否超级管理员")


class UserInfo(BaseModel):
    """当前用户信息"""
    id: int
    username: str
    real_name: str
    role: str
    is_super_admin: bool = False
    phone: str = ""
    email: str = ""
    is_active: bool = True

    class Config:
        from_attributes = True
