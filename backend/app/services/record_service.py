"""
上课记录管理服务
包含核心事务：审核通过时原子扣减课时
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course_type import CourseType
from app.models.lesson_record import LessonRecord
from app.models.package import Package
from app.models.student import Student
from app.models.teacher_student import TeacherStudent


async def get_records(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    teacher_id: Optional[int] = None,
    student_id: Optional[int] = None,
    parent_user_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    status: Optional[str] = None,
    exclude_status: Optional[str] = None,
) -> tuple[list[dict], int]:
    """
    获取上课记录列表（分页，多条件筛选）
    """
    base_query = (
        select(LessonRecord)
        .join(LessonRecord.student)
        .options(
            selectinload(LessonRecord.student).selectinload(Student.parent_user),
            selectinload(LessonRecord.teacher),
            selectinload(LessonRecord.course_type),
            selectinload(LessonRecord.reviewer),
        )
    )
    count_query = select(func.count(LessonRecord.id)).select_from(LessonRecord).join(LessonRecord.student)

    if teacher_id is not None:
        base_query = base_query.where(LessonRecord.teacher_id == teacher_id)
        count_query = count_query.where(LessonRecord.teacher_id == teacher_id)
    if student_id is not None:
        base_query = base_query.where(LessonRecord.student_id == student_id)
        count_query = count_query.where(LessonRecord.student_id == student_id)
    if parent_user_id is not None:
        base_query = base_query.where(Student.parent_user_id == parent_user_id)
        count_query = count_query.where(Student.parent_user_id == parent_user_id)
    if reviewer_id is not None:
        base_query = base_query.where(LessonRecord.reviewer_id == reviewer_id)
        count_query = count_query.where(LessonRecord.reviewer_id == reviewer_id)
    if status is not None:
        base_query = base_query.where(LessonRecord.status == status)
        count_query = count_query.where(LessonRecord.status == status)
    if exclude_status is not None:
        base_query = base_query.where(LessonRecord.status != exclude_status)
        count_query = count_query.where(LessonRecord.status != exclude_status)

    total = (await db.execute(count_query)).scalar() or 0

    base_query = (
        base_query
        .order_by(LessonRecord.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    records = (await db.execute(base_query)).scalars().all()

    record_list = []
    for r in records:
        record_list.append({
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student.name if r.student else "",
            "parent_name": r.student.parent_user.real_name if r.student and r.student.parent_user else "",
            "teacher_id": r.teacher_id,
            "teacher_name": r.teacher.real_name if r.teacher else "",
            "course_type_id": r.course_type_id,
            "course_type_name": r.course_type.name if r.course_type else "",
            "hours": float(r.hours),
            "content": r.content or "",
            "date": r.date,
            "status": r.status,
            "reviewer_id": r.reviewer_id,
            "reviewer_name": r.reviewer.real_name if r.reviewer else "",
            "review_comment": r.review_comment or "",
            "reviewed_at": r.reviewed_at,
            "created_at": r.created_at,
        })

    return record_list, total


async def get_pending_records(
    db: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[dict], int]:
    """获取待审核记录列表"""
    return await get_records(db, page=page, page_size=page_size, status="pending")


async def create_record(
    db: AsyncSession,
    teacher_id: int,
    student_id: int,
    course_type_id: int,
    hours: float,
    record_date: datetime,
    content: str = "",
    status: str = "pending",
) -> LessonRecord:
    """
    教师创建上课记录
    校验学生是否已分配给该教师
    """
    # 校验师生分配关系
    result = await db.execute(
        select(TeacherStudent).where(
            TeacherStudent.teacher_id == teacher_id,
            TeacherStudent.student_id == student_id,
        )
    )
    if not result.scalar_one_or_none():
        raise ValueError("该学生未分配给您，无法创建上课记录")

    # 校验上课时间不能是未来
    if record_date > datetime.now():
        raise ValueError("上课时间不能是未来时间")

    # 校验课程类型存在
    result = await db.execute(
        select(CourseType).where(CourseType.id == course_type_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("指定的课程类型不存在")

    record = LessonRecord(
        student_id=student_id,
        teacher_id=teacher_id,
        course_type_id=course_type_id,
        hours=hours,
        content=content,
        date=record_date,
        status=status,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def approve_record(
    db: AsyncSession,
    record_id: int,
    reviewer_id: int,
    comment: str = "",
) -> LessonRecord:
    """
    ★ 核心事务：审批通过上课记录，并原子性扣减课时

    事务流程：
    1. 锁定并读取记录
    2. 更新记录状态为 approved
    3. 查找同学生+同课程类型的有效课时包（按 expire_date ASC，FIFO 扣减）
    4. 锁定并扣减课时包
    5. 若课时不足，回滚事务并抛出异常
    6. 提交事务
    """
    from app.services.notification_service import create_notification

    # 1. 锁定并读取记录（含学生信息以获取其家长ID）
    result = await db.execute(
        select(LessonRecord)
        .options(selectinload(LessonRecord.student))
        .where(LessonRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise ValueError("上课记录不存在")
    if record.status != "pending":
        raise ValueError(f"只能审核待审核状态的记录，当前状态: {record.status}")

    # 获取该学生所属家长的ID
    if not record.student:
        raise ValueError("记录关联的学生不存在")
    parent_id = record.student.parent_user_id

    # 2. 更新记录状态
    record.status = "approved"
    record.reviewer_id = reviewer_id
    record.reviewed_at = datetime.now()
    record.review_comment = comment

    # 3. 扣减课时 — 优先级：先扣指定课程 → 再扣通用课时包
    #    FIFO：按 expire_date ASC（先到期先扣），FOR UPDATE 锁定防并发
    remaining = float(record.hours)

    # 3a. 先扣同课程类型的专用课时包
    result = await db.execute(
        select(Package)
        .where(
            Package.parent_user_id == parent_id,
            Package.course_type_id == record.course_type_id,
            Package.status == "active",
            Package.used_hours < Package.total_hours,
        )
        .order_by(Package.expire_date.asc())
        .with_for_update()
    )
    for pkg in result.scalars().all():
        avail = float(pkg.total_hours) - float(pkg.used_hours)
        deduct = min(avail, remaining)
        pkg.used_hours = float(pkg.used_hours) + deduct
        remaining -= deduct
        if float(pkg.used_hours) >= float(pkg.total_hours):
            pkg.status = "depleted"
        if remaining <= 0:
            break

    # 3b. 不够则扣通用课时包（course_type_id IS NULL）
    if remaining > 0:
        result = await db.execute(
            select(Package)
            .where(
                Package.parent_user_id == parent_id,
                Package.course_type_id.is_(None),
                Package.status == "active",
                Package.used_hours < Package.total_hours,
            )
            .order_by(Package.expire_date.asc())
            .with_for_update()
        )
        for pkg in result.scalars().all():
            avail = float(pkg.total_hours) - float(pkg.used_hours)
            deduct = min(avail, remaining)
            pkg.used_hours = float(pkg.used_hours) + deduct
            remaining -= deduct
            if float(pkg.used_hours) >= float(pkg.total_hours):
                pkg.status = "depleted"
            if remaining <= 0:
                break

    # 4. 课时不足，抛异常触发回滚（get_db 依赖会捕获并 rollback）
    if remaining > 0:
        raise ValueError(
            f"剩余课时不足！需要 {float(record.hours)} 小时，"
            f"当前可用课时缺少 {remaining} 小时"
        )

    # 5. 事务提交成功后，创建通知给教师
    await create_notification(
        db,
        user_id=record.teacher_id,
        title="上课记录已通过审核",
        content=(
            f"您为 {record.student.name if record.student else '学生'} "
            f"创建的 {record.hours} 小时上课记录已通过审核"
            f"{('，审核意见：' + comment) if comment else ''}"
        ),
        related_type="record",
        related_id=record.id,
    )

    # 重新加载记录（含关联数据）
    result = await db.execute(
        select(LessonRecord)
        .options(
            selectinload(LessonRecord.student),
            selectinload(LessonRecord.teacher),
            selectinload(LessonRecord.course_type),
        )
        .where(LessonRecord.id == record_id)
    )
    return result.scalar_one()


async def reject_record(
    db: AsyncSession,
    record_id: int,
    reviewer_id: int,
    comment: str = "",
) -> Optional[LessonRecord]:
    """
    驳回上课记录（不扣课时）
    """
    from app.services.notification_service import create_notification

    result = await db.execute(
        select(LessonRecord).where(LessonRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        return None
    if record.status != "pending":
        raise ValueError("只能审核待审核状态的记录")

    record.status = "rejected"
    record.reviewer_id = reviewer_id
    record.reviewed_at = datetime.now()
    record.review_comment = comment
    await db.commit()
    await db.refresh(record)

    # 通知教师
    await create_notification(
        db,
        user_id=record.teacher_id,
        title="上课记录已被驳回",
        content=(
            f"您创建的 {record.hours} 小时上课记录已被驳回"
            f"{('，原因：' + comment) if comment else ''}"
        ),
        related_type="record",
        related_id=record.id,
    )

    return record
