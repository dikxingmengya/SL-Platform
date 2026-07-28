"""
学生档案模型 (student 表)
每个学生归属于一个家长(parent_user_id)
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="学生姓名")
    parent_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="所属家长用户ID"
    )
    grade: Mapped[str] = mapped_column(String(20), default="", comment="年级")
    school: Mapped[str] = mapped_column(String(100), default="", comment="学校")
    notes: Mapped[str] = mapped_column(Text, default="", comment="备注")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否在读")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联关系
    parent_user: Mapped["User"] = relationship(
        "User", back_populates="children", foreign_keys=[parent_user_id]
    )
    # 关联的教师（多对多）
    teachers: Mapped[list["TeacherStudent"]] = relationship(
        "TeacherStudent", back_populates="student", cascade="all, delete-orphan"
    )
    # 上课记录列表
    lesson_records: Mapped[list["LessonRecord"]] = relationship(
        "LessonRecord", back_populates="student", cascade="all, delete-orphan"
    )
