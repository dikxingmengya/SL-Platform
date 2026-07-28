"""
应用配置模块
读取环境变量，提供全局配置常量
"""
import os
from typing import Optional


class Settings:
    """应用配置类，支持环境变量覆盖"""

    # 应用基本信息
    APP_NAME: str = "SL-Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # 数据库配置 (默认连接本地 MySQL)
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "123456")
    DB_NAME: str = os.getenv("DB_NAME", "sl_platform")

    @property
    def database_url(self) -> str:
        """构建异步数据库连接 URL"""
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    @property
    def database_url_sync(self) -> str:
        """构建同步数据库连接 URL（用于 alembic 等工具）"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    # JWT 认证配置
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "sl-platform-secret-key-change-in-production-2026"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 默认 24 小时

    # CORS 允许的前端地址
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # 分页默认值
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


# 全局单例配置
settings = Settings()
