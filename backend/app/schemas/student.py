"""
学生档案相关 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    """创建学生请求"""
    name: str = Field(..., min_length=1, max_length=50, description="学生姓名")
    parent_user_id: int = Field(..., gt=0, description="所属家长用户ID（必填）")
    grade: str = Field(default="", max_length=20, description="年级")
    school: str = Field(default="", max_length=100, description="学校")
    notes: str = Field(default="", description="备注")


class StudentUpdate(BaseModel):
    """更新学生请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="学生姓名")
    parent_user_id: Optional[int] = Field(default=None, gt=0, description="所属家长用户ID")
    grade: Optional[str] = Field(default=None, max_length=20, description="年级")
    school: Optional[str] = Field(default=None, max_length=100, description="学校")
    notes: Optional[str] = Field(default=None, description="备注")
    is_active: Optional[bool] = Field(default=None, description="是否在读")


class StudentOut(BaseModel):
    """学生列表项响应（含所属家长信息）"""
    id: int
    name: str
    parent_user_id: int
    parent_name: str = ""          # 家长姓名（JOIN 查询）
    parent_phone: str = ""         # 家长电话
    grade: str = ""
    school: str = ""
    notes: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
