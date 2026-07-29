"""
上课记录相关 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LessonRecordCreate(BaseModel):
    """创建上课记录请求"""
    student_id: int = Field(..., gt=0, description="上课学生ID")
    teacher_id: int = Field(default=0, gt=0, description="授课教师ID（管理员创建时指定，教师端自动取当前用户）")
    course_type_id: int = Field(..., gt=0, description="课程类型ID")
    hours: float = Field(..., gt=0, description="上课时长（小时）")
    content: str = Field(default="", description="上课内容/备注")
    date: datetime = Field(..., description="上课时间")
    status: str = Field(default="pending", description="状态: pending=提交审核, draft=保存草稿")


class LessonRecordReview(BaseModel):
    """审核上课记录请求"""
    comment: str = Field(default="", max_length=500, description="审核意见")


class LessonRecordOut(BaseModel):
    """上课记录列表项响应"""
    id: int
    student_id: int
    student_name: str = ""         # 学生姓名
    teacher_id: int
    teacher_name: str = ""         # 教师姓名
    course_type_id: int
    course_type_name: str = ""     # 课程名称
    hours: float
    content: str = ""
    date: datetime
    status: str = "pending"
    reviewer_id: Optional[int] = None
    reviewer_name: str = ""        # 审核人姓名
    review_comment: str = ""
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
