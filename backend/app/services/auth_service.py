"""
认证服务：登录验证、令牌管理
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import create_access_token, verify_password


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> dict | None:
    """
    验证用户名密码，成功返回含 token 的字典，失败返回 None
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    # 创建 JWT 令牌
    token = create_access_token(user_id=user.id, role=user.role)

    return {
        "token": token,
        "user_id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
    }
