"""
教师端接口路由 /api/teacher/*
教师权限：Depends(RoleChecker(['teacher']))
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lesson_record import LessonRecord
from app.models.user import User
from app.schemas.lesson_record import LessonRecordCreate
from app.services import (
    course_type_service,
    record_service,
    student_service,
    notification_service,
)
from app.utils.permissions import RoleChecker, get_current_user
from app.utils.response import paginated_response, success

router = APIRouter(prefix="/api/teacher", tags=["教师端"])

_teacher_check = Depends(RoleChecker(["teacher"]))


@router.get("/course-types", summary="获取课程类型列表", dependencies=[_teacher_check])
async def get_course_types(db: AsyncSession = Depends(get_db)):
    types = await course_type_service.get_course_types(db, active_only=True)
    ct_list = [{
        "id": t.id, "name": t.name, "description": t.description,
        "default_hourly_rate": float(t.default_hourly_rate), "is_active": t.is_active,
    } for t in types]
    return success(data=ct_list)


@router.get("/students", summary="我的学生列表", dependencies=[_teacher_check])
async def my_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    students = await student_service.get_students_by_teacher(db, teacher_id=current_user.id)
    return success(data=students)


@router.post("/records", summary="创建上课记录", dependencies=[_teacher_check])
async def create_record(
    data: LessonRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        record = await record_service.create_record(
            db,
            teacher_id=current_user.id,
            student_id=data.student_id,
            course_type_id=data.course_type_id,
            hours=data.hours,
            record_date=data.date,
            content=data.content,
            status=data.status,
        )
        msg = "草稿已保存" if data.status == "draft" else "上课记录已提交，等待审核"
        return success(data={"id": record.id, "status": record.status}, msg=msg)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/records", summary="我的上课记录", dependencies=[_teacher_check])
async def my_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records, total = await record_service.get_records(
        db, page=page, page_size=page_size, teacher_id=current_user.id, status=status
    )
    return paginated_response(items=records, total=total, page=page, page_size=page_size)


@router.put("/records/{record_id}/submit", summary="提交草稿", dependencies=[_teacher_check])
async def submit_draft(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(LessonRecord).where(
            LessonRecord.id == record_id,
            LessonRecord.teacher_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    if record.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能提交草稿状态的记录")
    record.status = "pending"
    await db.commit()
    return success(data={"id": record.id, "status": "pending"}, msg="草稿已提交审核")


@router.put("/records/{record_id}", summary="编辑草稿", dependencies=[_teacher_check])
async def update_draft(
    record_id: int,
    data: LessonRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """编辑草稿记录（仅 status=draft 且本人创建的可编辑）"""
    result = await db.execute(
        select(LessonRecord).where(
            LessonRecord.id == record_id,
            LessonRecord.teacher_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    if record.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能编辑草稿状态的记录")
    # 同时校验时间不为未来
    if data.date > datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上课时间不能是未来时间")

    record.student_id = data.student_id
    record.course_type_id = data.course_type_id
    record.hours = data.hours
    record.date = data.date
    record.content = data.content
    await db.commit()
    await db.refresh(record)
    return success(data={"id": record.id, "status": record.status}, msg="草稿已更新")


@router.get("/statistics", summary="个人统计", dependencies=[_teacher_check])
async def my_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records, total = await record_service.get_records(
        db, page=1, page_size=10000, teacher_id=current_user.id
    )
    pending = sum(1 for r in records if r["status"] == "pending")
    approved = sum(1 for r in records if r["status"] == "approved")
    rejected = sum(1 for r in records if r["status"] == "rejected")
    total_hours = sum(r["hours"] for r in records if r["status"] == "approved")
    students = await student_service.get_students_by_teacher(db, teacher_id=current_user.id)
    unread = await notification_service.get_unread_count(db, user_id=current_user.id)

    return success(data={
        "total_records": total,
        "pending_records": pending,
        "approved_records": approved,
        "rejected_records": rejected,
        "total_approved_hours": total_hours,
        "student_count": len(students),
        "unread_notifications": unread,
    })
