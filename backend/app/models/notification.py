"""
站内通知模型 (notification 表)
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Notification(Base):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="接收通知的用户ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="通知标题")
    content: Mapped[str] = mapped_column(Text, default="", comment="通知内容")
    is_read: Mapped[bool] = mapped_column(default=False, comment="是否已读")
    related_type: Mapped[str] = mapped_column(String(50), default="", comment="关联业务类型")
    related_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="关联业务ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 关联关系
    user: Mapped["User"] = relationship("User")
