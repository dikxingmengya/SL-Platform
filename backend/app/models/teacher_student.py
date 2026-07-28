"""
师生分配关联模型 (teacher_student 表)
多对多关联表：教师 ↔ 学生
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TeacherStudent(Base):
    __tablename__ = "teacher_student"
    __table_args__ = (
        UniqueConstraint("teacher_id", "student_id", name="uk_teacher_student"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="教师用户ID"
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False, comment="学生ID"
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="分配时间")

    # 关联关系
    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id])
    student: Mapped["Student"] = relationship("Student", back_populates="teachers")
