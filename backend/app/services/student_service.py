"""
学生档案管理服务
"""
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentCreate, StudentUpdate


async def get_student_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    parent_user_id: Optional[int] = None,
) -> tuple[list[dict], int]:
    """
    获取学生列表（分页，含家长信息）
    """
    base_query = select(Student).options(selectinload(Student.parent_user)).where(Student.is_active == True)
    count_query = select(func.count(Student.id)).where(Student.is_active == True)

    if parent_user_id is not None:
        base_query = base_query.where(Student.parent_user_id == parent_user_id)
        count_query = count_query.where(Student.parent_user_id == parent_user_id)

    # 总数
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    base_query = (
        base_query
        .order_by(Student.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    students = (await db.execute(base_query)).scalars().all()

    # 转换为字典列表
    student_list = []
    for s in students:
        student_list.append({
            "id": s.id,
            "name": s.name,
            "parent_user_id": s.parent_user_id,
            "parent_name": s.parent_user.real_name if s.parent_user else "",
            "parent_phone": s.parent_user.phone if s.parent_user else "",
            "grade": s.grade,
            "school": s.school,
            "notes": s.notes,
            "is_active": s.is_active,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        })

    return student_list, total


async def get_student_by_id(db: AsyncSession, student_id: int) -> Optional[Student]:
    """根据 ID 获取学生（含家长信息）"""
    result = await db.execute(
        select(Student)
        .options(selectinload(Student.parent_user))
        .where(Student.id == student_id)
    )
    return result.scalar_one_or_none()


async def create_student(db: AsyncSession, data: StudentCreate) -> Student:
    """
    创建学生档案
    校验 parent_user_id 对应的用户 role 必须为 parent
    """
    # 校验家长用户存在且角色正确
    result = await db.execute(select(User).where(User.id == data.parent_user_id))
    parent = result.scalar_one_or_none()
    if not parent:
        raise ValueError("指定的家长用户不存在")
    if parent.role != "parent":
        raise ValueError(f"用户 '{parent.real_name}' 的角色是 '{parent.role}'，不是家长")

    student = Student(
        name=data.name,
        parent_user_id=data.parent_user_id,
        grade=data.grade,
        school=data.school,
        notes=data.notes,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


async def update_student(
    db: AsyncSession, student_id: int, data: StudentUpdate
) -> Optional[Student]:
    """更新学生档案"""
    student = await get_student_by_id(db, student_id)
    if not student:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)

    await db.commit()
    await db.refresh(student)
    return student


async def delete_student(db: AsyncSession, student_id: int) -> bool:
    """软删除学生（设置 is_active=0）"""
    result = await db.execute(
        update(Student).where(Student.id == student_id).values(is_active=False)
    )
    await db.commit()
    return result.rowcount > 0


async def get_students_by_parent(
    db: AsyncSession, parent_user_id: int
) -> list[Student]:
    """
    获取某家长名下的所有孩子（家长端用）
    """
    result = await db.execute(
        select(Student)
        .where(Student.parent_user_id == parent_user_id)
        .order_by(Student.id)
    )
    return list(result.scalars().all())


async def get_students_by_teacher(
    db: AsyncSession, teacher_id: int
) -> list[dict]:
    """
    获取某教师分配的所有学生（教师端用，含家长联系方式）
    """
    from app.models.teacher_student import TeacherStudent

    result = await db.execute(
        select(TeacherStudent)
        .options(
            selectinload(TeacherStudent.student).selectinload(Student.parent_user)
        )
        .where(TeacherStudent.teacher_id == teacher_id)
    )
    assignments = result.scalars().all()

    student_list = []
    for ts in assignments:
        s = ts.student
        student_list.append({
            "assignment_id": ts.id,
            "student_id": s.id,
            "student_name": s.name,
            "student_grade": s.grade,
            "school": s.school,
            "parent_name": s.parent_user.real_name if s.parent_user else "",
            "parent_phone": s.parent_user.phone if s.parent_user else "",
            "assigned_at": ts.assigned_at,
        })

    return student_list
