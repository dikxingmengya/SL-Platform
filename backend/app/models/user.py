"""
用户模型 (user 表)
"""
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="登录用户名")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="bcrypt 密码哈希")
    real_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="真实姓名")
    role: Mapped[str] = mapped_column(
        Enum("admin", "teacher", "parent", name="user_role_enum"),
        nullable=False,
        comment="角色"
    )
    is_super_admin: Mapped[bool] = mapped_column(default=False, comment="是否超级管理员")
    phone: Mapped[str] = mapped_column(String(20), default="", comment="手机号")
    email: Mapped[str] = mapped_column(String(100), default="", comment="邮箱")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关联关系
    teacher_profile: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    # 家长关联的学生列表
    children: Mapped[list["Student"]] = relationship(
        "Student", back_populates="parent_user", foreign_keys="Student.parent_user_id"
    )
