"""
师生分配相关 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TeacherStudentCreate(BaseModel):
    """创建师生分配请求"""
    teacher_id: int = Field(..., gt=0, description="教师用户ID")
    student_id: int = Field(..., gt=0, description="学生ID")


class TeacherStudentOut(BaseModel):
    """师生分配列表项响应"""
    id: int
    teacher_id: int
    teacher_name: str = ""         # 教师姓名
    teacher_phone: str = ""        # 教师电话
    teacher_subject: str = ""      # 教师擅长科目
    student_id: int
    student_name: str = ""         # 学生姓名
    student_grade: str = ""        # 学生年级
    parent_name: str = ""          # 家长姓名
    assigned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeacherStudentSimple(BaseModel):
    """简化的师生分配（教师端用）"""
    id: int
    student_id: int
    student_name: str = ""
    student_grade: str = ""
    parent_name: str = ""
    parent_phone: str = ""
    assigned_at: Optional[datetime] = None

    class Config:
        from_attributes = True
