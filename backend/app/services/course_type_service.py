"""
课程类型管理服务
"""
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course_type import CourseType
from app.schemas.course_type import CourseTypeCreate, CourseTypeUpdate


async def get_course_types(db: AsyncSession, active_only: bool = False) -> list[CourseType]:
    """获取课程类型列表"""
    q = select(CourseType).order_by(CourseType.id)
    if active_only:
        q = q.where(CourseType.is_active == True)
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_course_type_by_id(db: AsyncSession, ct_id: int) -> Optional[CourseType]:
    """根据 ID 获取课程类型"""
    result = await db.execute(select(CourseType).where(CourseType.id == ct_id))
    return result.scalar_one_or_none()


async def create_course_type(db: AsyncSession, data: CourseTypeCreate) -> CourseType:
    """创建课程类型"""
    ct = CourseType(
        name=data.name,
        description=data.description,
        default_hourly_rate=data.default_hourly_rate,
    )
    db.add(ct)
    await db.commit()
    await db.refresh(ct)
    return ct


async def update_course_type(
    db: AsyncSession, ct_id: int, data: CourseTypeUpdate
) -> Optional[CourseType]:
    """更新课程类型"""
    ct = await get_course_type_by_id(db, ct_id)
    if not ct:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ct, key, value)

    await db.commit()
    await db.refresh(ct)
    return ct


async def delete_course_type(db: AsyncSession, ct_id: int) -> bool:
    """软删除课程类型（关联数据保护）"""
    result = await db.execute(
        update(CourseType).where(CourseType.id == ct_id).values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0
