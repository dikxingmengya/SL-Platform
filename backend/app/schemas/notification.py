"""
站内通知相关 Pydantic 模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationOut(BaseModel):
    """通知列表项响应"""
    id: int
    user_id: int
    title: str
    content: str = ""
    is_read: bool = False
    related_type: str = ""
    related_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
