"""
用户相关 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    role: str = Field(..., description="角色：admin/teacher/parent")
    phone: str = Field(default="", max_length=20, description="手机号")
    email: str = Field(default="", max_length=100, description="邮箱")
    # 教师专用字段
    subject: str = Field(default="", max_length=100, description="擅长科目（仅教师）")
    bio: str = Field(default="", description="个人简介（仅教师）")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("admin", "teacher", "parent"):
            raise ValueError("角色必须为 admin、teacher 或 parent")
        return v


class UserUpdate(BaseModel):
    """更新用户请求"""
    real_name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="真实姓名")
    role: Optional[str] = Field(default=None, description="角色：admin/teacher/parent")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    password: Optional[str] = Field(default=None, min_length=6, max_length=100, description="新密码（可选）")
    admin_password: Optional[str] = Field(default=None, min_length=1, description="修改密码时需验证管理员密码")
    is_active: Optional[bool] = Field(default=None, description="是否启用")
    # 教师专用字段
    subject: Optional[str] = Field(default=None, max_length=100, description="擅长科目")
    bio: Optional[str] = Field(default=None, description="个人简介")


class UserOut(BaseModel):
    """用户列表项响应"""
    id: int
    username: str
    real_name: str
    role: str
    phone: str
    email: str
    is_active: bool
    created_at: Optional[datetime] = None
    # 教师扩展字段
    subject: str = ""
    bio: str = ""

    class Config:
        from_attributes = True
