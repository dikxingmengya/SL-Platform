"""
课时包模型 (package 表)
归属于家长（parent_user_id），名下所有孩子共享
"""
from datetime import date, datetime

from typing import Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Package(Base):
    __tablename__ = "package"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="归属家长用户ID"
    )
    course_type_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("course_type.id"), nullable=True, comment="课程类型ID，NULL表示通用课时"
    )
    total_hours: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, comment="总课时")
    used_hours: Mapped[float] = mapped_column(Numeric(8, 2), default=0.00, comment="已消耗课时")
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, comment="购买金额")
    expire_date: Mapped[date] = mapped_column(Date, nullable=True, comment="有效期截止日")
    status: Mapped[str] = mapped_column(
        Enum("active", "expired", "depleted", name="package_status_enum"),
        default="active",
        comment="状态",
    )
    notes: Mapped[str] = mapped_column(String(500), default="", comment="备注")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # 关联关系
    parent_user: Mapped["User"] = relationship("User", foreign_keys=[parent_user_id])
    course_type: Mapped[Optional["CourseType"]] = relationship("CourseType")

    @property
    def remaining_hours(self) -> float:
        """计算剩余课时"""
        return max(0, float(self.total_hours) - float(self.used_hours))
