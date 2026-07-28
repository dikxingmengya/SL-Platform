/**
 * Vue Router 路由配置
 * 包含路由守卫：检查登录状态和角色权限
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 登录页（无需守卫）
import Login from '@/views/Login.vue'

// 布局组件（懒加载）
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const TeacherLayout = () => import('@/layouts/TeacherLayout.vue')
const ParentLayout = () => import('@/layouts/ParentLayout.vue')

// 管理端页面（懒加载）
const AdminDashboard = () => import('@/views/admin/Dashboard.vue')
const UserManagement = () => import('@/views/admin/UserManagement.vue')
const StudentManagement = () => import('@/views/admin/StudentManagement.vue')
const TeacherStudent = () => import('@/views/admin/TeacherStudent.vue')
const CourseTypeManagement = () => import('@/views/admin/CourseTypeManagement.vue')
const PackageManagement = () => import('@/views/admin/PackageManagement.vue')
const RecordReview = () => import('@/views/admin/RecordReview.vue')
const AdminStatistics = () => import('@/views/admin/Statistics.vue')

// 教师端页面
const TeacherDashboard = () => import('@/views/teacher/Dashboard.vue')
const MyStudents = () => import('@/views/teacher/MyStudents.vue')
const RecordCreate = () => import('@/views/teacher/RecordCreate.vue')
const MyRecords = () => import('@/views/teacher/MyRecords.vue')
const TeacherStatistics = () => import('@/views/teacher/Statistics.vue')

// 家长端页面
const ParentDashboard = () => import('@/views/parent/Dashboard.vue')
const ChildPackages = () => import('@/views/parent/ChildPackages.vue')
const ChildRecords = () => import('@/views/parent/ChildRecords.vue')
const ChildTeachers = () => import('@/views/parent/ChildTeachers.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' },
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { role: 'admin', title: '管理端' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', component: AdminDashboard, meta: { title: '首页概览' } },
      { path: 'users', component: UserManagement, meta: { title: '用户管理' } },
      { path: 'students', component: StudentManagement, meta: { title: '学生管理' } },
      { path: 'teacher-students', component: TeacherStudent, meta: { title: '师生分配' } },
      { path: 'course-types', component: CourseTypeManagement, meta: { title: '课程类型' } },
      { path: 'packages', component: PackageManagement, meta: { title: '课时包管理' } },
      { path: 'records', component: RecordReview, meta: { title: '记录审核' } },
      { path: 'statistics', component: AdminStatistics, meta: { title: '统计报表' } },
    ],
  },
  {
    path: '/teacher',
    component: TeacherLayout,
    meta: { role: 'teacher', title: '教师端' },
    children: [
      { path: '', redirect: '/teacher/dashboard' },
      { path: 'dashboard', component: TeacherDashboard, meta: { title: '首页' } },
      { path: 'students', component: MyStudents, meta: { title: '我的学生' } },
      { path: 'records/create', component: RecordCreate, meta: { title: '创建记录' } },
      { path: 'records', component: MyRecords, meta: { title: '我的记录' } },
      { path: 'statistics', component: TeacherStatistics, meta: { title: '个人统计' } },
    ],
  },
  {
    path: '/parent',
    component: ParentLayout,
    meta: { role: 'parent', title: '家长端' },
    children: [
      { path: '', redirect: '/parent/dashboard' },
      { path: 'dashboard', component: ParentDashboard, meta: { title: '我的孩子' } },
      { path: 'packages', component: ChildPackages, meta: { title: '课时明细' } },
      { path: 'children/:id/records', component: ChildRecords, meta: { title: '上课记录' } },
      { path: 'children/:id/teachers', component: ChildTeachers, meta: { title: '授课教师' } },
    ],
  },
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ==================== 路由守卫 ====================
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  document.title = (to.meta.title as string) || 'SL-Platform'

  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') || ''

  // 登录页：已登录→跳转角色首页，未登录→放行
  if (to.path === '/login') {
    if (token && role) {
      const roleMap: Record<string, string> = {
        admin: '/admin/dashboard',
        teacher: '/teacher/dashboard',
        parent: '/parent/dashboard',
      }
      const target = roleMap[role]
      if (target) {
        next({ path: target, replace: true })
        return
      }
    }
    next()
    return
  }

  // 未登录 → 跳转登录页
  if (!token) {
    next({ path: '/login', replace: true })
    return
  }

  // 检查角色权限
  const requiredRole = to.meta.role as string
  if (requiredRole && role !== requiredRole) {
    const roleMap: Record<string, string> = {
      admin: '/admin/dashboard',
      teacher: '/teacher/dashboard',
      parent: '/parent/dashboard',
    }
    const target = roleMap[role]
    if (target) {
      next({ path: target, replace: true })
      return
    }
    // 角色未知 → 清除 token 去登录
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    next({ path: '/login', replace: true })
    return
  }

  next()
})

export default router
