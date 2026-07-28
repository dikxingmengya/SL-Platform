"""
用户管理服务：CRUD 操作
"""
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


async def get_user_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    role: Optional[str] = None,
) -> tuple[list[dict], int]:
    """
    获取用户列表（分页，支持角色过滤）
    返回 (用户字典列表, 总记录数)
    """
    # 基础查询（默认只显示启用用户）
    base_query = select(User).where(User.is_active == True)
    count_query = select(func.count(User.id)).where(User.is_active == True)

    if role:
        base_query = base_query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    # 查询总数
    total = (await db.execute(count_query)).scalar() or 0

    # 分页查询（左连接 teacher 表）
    base_query = (
        base_query
        .options(selectinload(User.teacher_profile))
        .order_by(User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    users = (await db.execute(base_query)).scalars().all()

    # 转换为字典列表（含 teacher 扩展字段）
    user_list = []
    for u in users:
        user_dict = {
            "id": u.id,
            "username": u.username,
            "real_name": u.real_name,
            "role": u.role,
            "phone": u.phone,
            "email": u.email,
            "is_active": u.is_active,
            "is_super_admin": u.is_super_admin,
            "created_at": u.created_at,
            "subject": u.teacher_profile.subject if u.teacher_profile else "",
            "bio": u.teacher_profile.bio if u.teacher_profile else "",
        }
        user_list.append(user_dict)

    return user_list, total


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据 ID 获取用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """
    创建新用户（含角色校验和教师扩展信息）
    """
    # 检查用户名唯一性
    existing = await get_user_by_username(db, data.username)
    if existing:
        raise ValueError(f"用户名 '{data.username}' 已存在")

    # 创建用户
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        real_name=data.real_name,
        role=data.role,
        phone=data.phone,
        email=data.email,
    )
    db.add(user)
    await db.flush()  # 获取 user.id

    # 如果是教师，创建教师扩展记录
    if data.role == "teacher":
        teacher = Teacher(
            user_id=user.id,
            subject=data.subject,
            bio=data.bio,
        )
        db.add(teacher)

    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: int, data: UserUpdate) -> Optional[User]:
    """
    更新用户信息
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None

    # 更新基础字段（仅更新传入的非空字段）
    update_data = data.model_dump(exclude_unset=True)

    # 分离教师专用字段
    teacher_fields = {}
    for field in ("subject", "bio"):
        if field in update_data:
            teacher_fields[field] = update_data.pop(field)

    # 如果包含密码，进行哈希
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    # 更新 User 表
    if update_data:
        for key, value in update_data.items():
            setattr(user, key, value)

    # 更新 Teacher 表
    if teacher_fields and user.role == "teacher":
        result = await db.execute(select(Teacher).where(Teacher.user_id == user_id))
        teacher = result.scalar_one_or_none()
        if teacher:
            for key, value in teacher_fields.items():
                setattr(teacher, key, value)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """软删除用户（设置 is_active=0）"""
    result = await db.execute(
        update(User).where(User.id == user_id).values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0
