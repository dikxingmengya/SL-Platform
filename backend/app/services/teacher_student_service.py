"""
师生分配管理服务
"""
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.student import Student
from app.models.teacher_student import TeacherStudent
from app.models.user import User
from app.schemas.teacher_student import TeacherStudentCreate


async def get_assignments(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    teacher_id: Optional[int] = None,
    student_id: Optional[int] = None,
) -> tuple[list[dict], int]:
    """
    获取师生分配列表（分页）
    """
    base_query = (
        select(TeacherStudent)
        .options(
            selectinload(TeacherStudent.teacher).selectinload(User.teacher_profile),
            selectinload(TeacherStudent.student).selectinload(Student.parent_user),
        )
    )
    count_query = select(func.count(TeacherStudent.id))

    if teacher_id is not None:
        base_query = base_query.where(TeacherStudent.teacher_id == teacher_id)
        count_query = count_query.where(TeacherStudent.teacher_id == teacher_id)
    if student_id is not None:
        base_query = base_query.where(TeacherStudent.student_id == student_id)
        count_query = count_query.where(TeacherStudent.student_id == student_id)

    total = (await db.execute(count_query)).scalar() or 0

    base_query = (
        base_query
        .order_by(TeacherStudent.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    assignments = (await db.execute(base_query)).scalars().all()

    assignment_list = []
    for a in assignments:
        assignment_list.append({
            "id": a.id,
            "teacher_id": a.teacher_id,
            "teacher_name": a.teacher.real_name if a.teacher else "",
            "teacher_phone": a.teacher.phone if a.teacher else "",
            "teacher_subject": (
                a.teacher.teacher_profile.subject
                if a.teacher and a.teacher.teacher_profile else ""
            ),
            "student_id": a.student_id,
            "student_name": a.student.name if a.student else "",
            "student_grade": a.student.grade if a.student else "",
            "parent_name": (
                a.student.parent_user.real_name
                if a.student and a.student.parent_user else ""
            ),
            "assigned_at": a.assigned_at,
        })

    return assignment_list, total


async def create_assignment(
    db: AsyncSession, data: TeacherStudentCreate
) -> TeacherStudent:
    """
    创建师生分配关系
    校验教师和学生均存在，且教师角色为 teacher
    """
    # 校验教师存在
    result = await db.execute(select(User).where(User.id == data.teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise ValueError("指定的教师不存在")
    if teacher.role != "teacher":
        raise ValueError(f"用户 '{teacher.real_name}' 不是教师角色")

    # 校验学生存在
    result = await db.execute(select(Student).where(Student.id == data.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise ValueError("指定的学生不存在")

    # 检查是否已存在分配
    result = await db.execute(
        select(TeacherStudent).where(
            TeacherStudent.teacher_id == data.teacher_id,
            TeacherStudent.student_id == data.student_id,
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("该师生分配关系已存在")

    assignment = TeacherStudent(
        teacher_id=data.teacher_id,
        student_id=data.student_id,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def delete_assignment(db: AsyncSession, assignment_id: int) -> bool:
    """删除师生分配关系"""
    result = await db.execute(
        delete(TeacherStudent).where(TeacherStudent.id == assignment_id)
    )
    await db.commit()
    return result.rowcount > 0
