"""
SL-Platform 家教课时管理系统 - FastAPI 应用入口
启动方式: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.models import *  # noqa: F401, F403 确保所有模型被导入
# 导入路由模块 — 直接 import router 避免与 models 下的同名模块冲突
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.teacher import router as teacher_router
from app.api.parent import router as parent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时：测试数据库连接
    关闭时：释放引擎连接池
    """
    # 启动时
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"[OK] 数据库连接成功: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    except Exception as e:
        print(f"[WARN] 数据库连接失败: {e}")
        print("      请检查 config.py 中的数据库配置，并确保执行了 init_db.sql")
    yield
    # 关闭时
    await engine.dispose()
    print("[INFO] SL-Platform 已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="SL-Platform 家教课时管理系统",
    version=settings.APP_VERSION,
    description="家长-学生分离的家教课时管理平台，支持管理端/教师端/家长端三端",
    lifespan=lifespan,
)

# 配置 CORS（允许前端开发服务器跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由模块
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(teacher_router)
app.include_router(parent_router)


@app.get("/", tags=["系统"])
async def root():
    """根路径：返回系统信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.APP_VERSION}
