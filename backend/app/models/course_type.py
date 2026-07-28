"""
课程类型模型 (course_type 表)
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CourseType(Base):
    __tablename__ = "course_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="课程名称")
    description: Mapped[str] = mapped_column(String(200), default="", comment="课程描述")
    default_hourly_rate: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0.00, comment="默认课时费"
    )
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
