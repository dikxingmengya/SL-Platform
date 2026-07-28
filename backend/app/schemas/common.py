"""
通用 Pydantic 模型：分页参数、统一响应
"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """分页查询参数"""
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=500, description="每页数量")


class PaginatedData(BaseModel, Generic[T]):
    """分页数据结构"""
    items: list[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = Field(default=0, description="状态码，0表示成功")
    msg: str = Field(default="success", description="提示信息")
    data: Optional[T] = Field(default=None, description="响应数据")
