"""
课时包相关 Pydantic 模型
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class PackageCreate(BaseModel):
    """购买/创建课时包请求"""
    parent_user_id: int = Field(..., gt=0, description="归属家长用户ID")
    course_type_id: Optional[int] = Field(default=None, description="课程类型ID，None=通用课时")
    total_hours: float = Field(..., gt=0, description="总课时数")
    price: float = Field(default=0.00, ge=0, description="购买金额")
    expire_date: Optional[date] = Field(default=None, description="有效期截止日")
    notes: str = Field(default="", max_length=500, description="备注")


class PackageUpdate(BaseModel):
    """手动调整课时包请求"""
    total_hours: Optional[float] = Field(default=None, gt=0, description="总课时数")
    used_hours: Optional[float] = Field(default=None, ge=0, description="已消耗课时数")
    price: Optional[float] = Field(default=None, ge=0, description="购买金额")
    expire_date: Optional[date] = Field(default=None, description="有效期截止日")
    status: Optional[str] = Field(default=None, description="状态: active/expired/depleted")
    notes: Optional[str] = Field(default=None, max_length=500, description="备注")

    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("active", "expired", "depleted"):
            raise ValueError("状态必须为 active、expired 或 depleted")
        return v


class PackageOut(BaseModel):
    """课时包列表项响应"""
    id: int
    parent_user_id: int
    parent_name: str = ""          # 家长姓名（JOIN）
    course_type_id: int
    course_type_name: str = ""     # 课程名称（JOIN）
    total_hours: float
    used_hours: float = 0.00
    remaining_hours: float = 0.00  # 计算的剩余课时
    price: float = 0.00
    expire_date: Optional[date] = None
    status: str = "active"
    notes: str = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
