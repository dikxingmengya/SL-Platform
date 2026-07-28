# ORM 模型包
from app.database import Base  # noqa: F401

# 按依赖顺序导入，确保表关系正常注册
from app.models.user import User  # noqa: F401
from app.models.teacher import Teacher  # noqa: F401
from app.models.student import Student  # noqa: F401
from app.models.teacher_student import TeacherStudent  # noqa: F401
from app.models.course_type import CourseType  # noqa: F401
from app.models.package import Package  # noqa: F401
from app.models.lesson_record import LessonRecord  # noqa: F401
from app.models.notification import Notification  # noqa: F401
