"""
上课记录模型 (lesson_record 表)
由教师创建，需管理员审核通过后才计入课时消耗
"""
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LessonRecord(Base):
    __tablename__ = "lesson_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("student.id"), nullable=False, comment="上课学生ID"
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, comment="授课教师ID"
    )
    course_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("course_type.id"), nullable=False, comment="课程类型ID"
    )
    hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, comment="上课时长(小时)")
    content: Mapped[str] = mapped_column(Text, default="", comment="上课内容/备注")
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="上课时间")
    status: Mapped[str] = mapped_column(
        Enum("draft", "pending", "approved", "rejected", name="record_status_enum"),
        default="pending",
        comment="审核状态",
    )
    reviewer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True, comment="审核人ID"
    )
    review_comment: Mapped[str] = mapped_column(String(500), default="", comment="审核意见")
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="审核时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关联关系
    student: Mapped["Student"] = relationship("Student", back_populates="lesson_records")
    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id])
    course_type: Mapped["CourseType"] = relationship("CourseType")
    reviewer: Mapped["User | None"] = relationship("User", foreign_keys=[reviewer_id])
