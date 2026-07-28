"""
站内通知服务
"""
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    content: str = "",
    related_type: str = "",
    related_id: Optional[int] = None,
) -> Notification:
    """
    创建站内通知
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        related_type=related_type,
        related_id=related_id,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_notifications(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
) -> tuple[list[Notification], int]:
    """
    获取用户通知列表（分页）
    """
    base_query = select(Notification).where(Notification.user_id == user_id)
    count_query = select(func.count(Notification.id)).where(
        Notification.user_id == user_id
    )

    if unread_only:
        base_query = base_query.where(Notification.is_read == False)
        count_query = count_query.where(Notification.is_read == False)

    total = (await db.execute(count_query)).scalar() or 0

    base_query = (
        base_query
        .order_by(Notification.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(base_query)
    notifications = result.scalars().all()

    return list(notifications), total


async def mark_as_read(db: AsyncSession, notification_id: int, user_id: int) -> bool:
    """标记通知为已读"""
    result = await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    await db.commit()
    return result.rowcount > 0


async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
    """标记用户所有通知为已读，返回更新数量"""
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return result.rowcount


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    """获取用户未读通知数量"""
    count = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
    )
    return count.scalar() or 0
