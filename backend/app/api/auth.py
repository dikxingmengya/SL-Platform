"""
认证接口路由
POST /api/auth/login  - 用户登录
GET  /api/auth/me     - 获取当前用户信息
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth_service import authenticate_user
from app.utils.permissions import get_current_user
from app.utils.response import success

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", summary="用户登录")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    用户名 + 密码登录，返回 JWT 令牌
    """
    result = await authenticate_user(db, request.username, request.password)
    if result is None:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误，或账号已被禁用",
        )

    return success(data=LoginResponse(**result).model_dump())


@router.get("/me", summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    返回当前登录用户的详细信息
    """
    user_info = UserInfo.model_validate(current_user)
    return success(data=user_info.model_dump())
