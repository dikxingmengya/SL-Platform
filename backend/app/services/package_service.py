"""
课时包管理服务
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course_type import CourseType
from app.models.package import Package
from app.models.user import User
from app.schemas.package import PackageCreate, PackageUpdate


async def get_packages(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    parent_user_id: Optional[int] = None,
) -> tuple[list[dict], int]:
    """
    获取课时包列表（分页）
    """
    base_query = (
        select(Package)
        .options(
            selectinload(Package.parent_user),
            selectinload(Package.course_type),
        )
    )
    count_query = select(func.count(Package.id))

    if parent_user_id is not None:
        base_query = base_query.where(Package.parent_user_id == parent_user_id)
        count_query = count_query.where(Package.parent_user_id == parent_user_id)

    total = (await db.execute(count_query)).scalar() or 0

    base_query = (
        base_query
        .order_by(Package.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    packages = (await db.execute(base_query)).scalars().all()

    package_list = []
    for p in packages:
        remaining = max(0, float(p.total_hours) - float(p.used_hours))
        package_list.append({
            "id": p.id,
            "parent_user_id": p.parent_user_id,
            "parent_name": p.parent_user.real_name if p.parent_user else "",
            "course_type_id": p.course_type_id,
            "course_type_name": p.course_type.name if p.course_type else "通用",
            "total_hours": float(p.total_hours),
            "used_hours": float(p.used_hours),
            "remaining_hours": remaining,
            "price": float(p.price),
            "expire_date": p.expire_date,
            "status": p.status,
            "notes": p.notes,
            "created_at": p.created_at,
        })

    return package_list, total


async def get_parent_packages(
    db: AsyncSession, parent_user_id: int
) -> list[dict]:
    """
    获取某个家长的课时包详情（家长端用）
    返回包含剩余课时信息的列表
    """
    result = await db.execute(
        select(Package)
        .options(selectinload(Package.course_type))
        .where(Package.parent_user_id == parent_user_id)
        .order_by(Package.expire_date.asc())
    )
    packages = result.scalars().all()

    package_list = []
    for p in packages:
        remaining = max(0, float(p.total_hours) - float(p.used_hours))
        package_list.append({
            "id": p.id,
            "parent_user_id": p.parent_user_id,
            "course_type_id": p.course_type_id,
            "course_type_name": p.course_type.name if p.course_type else "通用",
            "total_hours": float(p.total_hours),
            "used_hours": float(p.used_hours),
            "remaining_hours": remaining,
            "price": float(p.price),
            "expire_date": str(p.expire_date) if p.expire_date else None,
            "status": p.status,
            "notes": p.notes,
            "created_at": p.created_at,
        })

    return package_list


async def create_package(db: AsyncSession, data: PackageCreate) -> Package:
    """
    购买课时包
    校验家长用户存在且角色为 parent
    """
    # 校验家长用户存在且角色正确
    result = await db.execute(select(User).where(User.id == data.parent_user_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise ValueError("指定的家长用户不存在")
    if parent.role != "parent":
        raise ValueError(f"用户 '{parent.real_name}' 不是家长角色")

    # 校验课程类型存在（通用课时包跳过）
    if data.course_type_id is not None:
        result = await db.execute(
            select(CourseType).where(CourseType.id == data.course_type_id)
        )
        ct = result.scalar_one_or_none()
        if not ct:
            raise ValueError("指定的课程类型不存在")

    package = Package(
        parent_user_id=data.parent_user_id,
        course_type_id=data.course_type_id,
        total_hours=data.total_hours,
        used_hours=0.00,
        price=data.price,
        expire_date=data.expire_date,
        notes=data.notes,
        status="active",
    )
    db.add(package)
    await db.commit()
    await db.refresh(package)
    return package


async def update_package(
    db: AsyncSession, package_id: int, data: PackageUpdate
) -> Optional[Package]:
    """手动调整课时包"""
    result = await db.execute(select(Package).where(Package.id == package_id))
    package = result.scalar_one_or_none()
    if not package:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(package, key, value)

    await db.commit()
    await db.refresh(package)
    return package

async def delete_package(db: AsyncSession, package_id: int) -> bool:
    """删除课时包"""
    from sqlalchemy import delete as sqla_delete
    result = await db.execute(
        sqla_delete(Package).where(Package.id == package_id)
    )
    await db.commit()
    return result.rowcount > 0
