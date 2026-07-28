"""
统一响应格式工具模块
所有 API 返回统一格式: {"code": 0, "msg": "success", "data": {...}}
"""
from typing import Any, Optional


def success(data: Any = None, msg: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "msg": msg, "data": data}


def error(msg: str = "error", code: int = 1, data: Any = None) -> dict:
    """错误响应"""
    return {"code": code, "msg": msg, "data": data}


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
) -> dict:
    """分页响应"""
    return success({
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
    })
