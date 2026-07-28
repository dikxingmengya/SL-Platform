"""
课程类型相关 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CourseTypeCreate(BaseModel):
    """创建课程类型请求"""
    name: str = Field(..., min_length=1, max_length=50, description="课程名称")
    description: str = Field(default="", max_length=200, description="课程描述")
    default_hourly_rate: float = Field(default=0.00, ge=0, description="默认课时费")


class CourseTypeUpdate(BaseModel):
    """更新课程类型请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="课程名称")
    description: Optional[str] = Field(default=None, max_length=200, description="课程描述")
    default_hourly_rate: Optional[float] = Field(default=None, ge=0, description="默认课时费")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class CourseTypeOut(BaseModel):
    """课程类型列表项响应"""
    id: int
    name: str
    description: str = ""
    default_hourly_rate: float = 0.00
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
