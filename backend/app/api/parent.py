"""
家长端接口路由 /api/parent/*
家长权限：Depends(RoleChecker(['parent']))
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services import (
    package_service,
    record_service,
    student_service,
    notification_service,
    teacher_student_service,
)
from app.utils.permissions import RoleChecker, get_current_user
from app.utils.response import paginated_response, success

router = APIRouter(prefix="/api/parent", tags=["家长端"])

# 所有家长端接口需要 parent 角色（路由级别依赖）
_parent_check = Depends(RoleChecker(["parent"]))


@router.get("/children", summary="我的孩子列表", dependencies=[_parent_check])
async def my_children(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取当前家长名下所有孩子（student.parent_user_id = 当前用户ID）
    """
    children = await student_service.get_students_by_parent(
        db, parent_user_id=current_user.id
    )
    child_list = [{
        "id": c.id,
        "name": c.name,
        "grade": c.grade,
        "school": c.school,
        "notes": c.notes,
        "is_active": c.is_active,
        "created_at": str(c.created_at) if c.created_at else None,
    } for c in children]
    return success(data=child_list)


@router.get("/packages", summary="我的课时包明细", dependencies=[_parent_check])
async def my_packages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查看当前家长的课时包详情，含剩余课时
    课时包归属家长，名下所有孩子共享
    """
    packages = await package_service.get_parent_packages(db, parent_user_id=current_user.id)
    return success(data={
        "packages": packages,
    })


@router.get("/children/{student_id}/records", summary="孩子上课记录", dependencies=[_parent_check])
async def child_records(
    student_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查看某个孩子的上课记录历史（分页）
    校验该孩子属于当前家长
    """
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
    if student.parent_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该学生的信息")

    records, total = await record_service.get_records(
        db, page=page, page_size=page_size, student_id=student_id,
        exclude_status="rejected",  # 家长端不显示已驳回记录
    )
    return paginated_response(items=records, total=total, page=page, page_size=page_size)


@router.get("/children/{student_id}/teachers", summary="孩子分配的教师", dependencies=[_parent_check])
async def child_teachers(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查看某个孩子分配了哪些教师
    校验该孩子属于当前家长
    """
    student = await student_service.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
    if student.parent_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权查看该学生的信息")

    assignments, _ = await teacher_student_service.get_assignments(
        db, page=1, page_size=100, student_id=student_id
    )
    teachers = [{
        "teacher_id": a["teacher_id"],
        "teacher_name": a["teacher_name"],
        "teacher_phone": a["teacher_phone"],
        "teacher_subject": a["teacher_subject"],
        "assigned_at": str(a["assigned_at"]) if a.get("assigned_at") else None,
    } for a in assignments]

    return success(data={
        "student": {"id": student.id, "name": student.name},
        "teachers": teachers,
    })


@router.get("/notifications", summary="我的通知", dependencies=[_parent_check])
async def my_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前家长的通知列表"""
    notifications, total = await notification_service.get_notifications(
        db, user_id=current_user.id, page=page, page_size=page_size,
        unread_only=unread_only
    )
    notif_list = [{
        "id": n.id,
        "title": n.title,
        "content": n.content,
        "is_read": n.is_read,
        "related_type": n.related_type,
        "related_id": n.related_id,
        "created_at": str(n.created_at) if n.created_at else None,
    } for n in notifications]
    return paginated_response(items=notif_list, total=total, page=page, page_size=page_size)
