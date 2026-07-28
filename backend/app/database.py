"""
数据库引擎和会话管理模块
使用 SQLAlchemy 2.0 异步引擎
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,        # 调试模式下打印 SQL
    pool_size=10,               # 连接池大小
    max_overflow=20,            # 最大溢出连接数
    pool_pre_ping=True,         # 每次从池中取出时先 ping 检测连接有效性
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,     # 提交后不使对象过期，便于后续访问
)


# SQLAlchemy 声明式基类
class Base(DeclarativeBase):
    """所有 ORM 模型继承的基类"""
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI 依赖注入：获取数据库会话
    用法: db: AsyncSession = Depends(get_db)
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库：创建所有表（开发环境用，生产环境请使用 alembic 或 SQL 脚本）
    """
    async with engine.begin() as conn:
        # 导入所有模型以确保它们注册到 Base.metadata
        from app.models import user, teacher, student, teacher_student  # noqa: F401
        from app.models import course_type, package, lesson_record, notification  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
