"""
教师扩展信息模型 (teacher 表)
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Teacher(Base):
    __tablename__ = "teacher"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, comment="关联用户ID"
    )
    subject: Mapped[str] = mapped_column(String(100), default="", comment="擅长科目")
    bio: Mapped[str] = mapped_column(Text, default="", comment="个人简介")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="teacher_profile")
