/**
 * 管理端 API
 */
import request from './request'

export const adminApi = {
  // ===== 用户管理 =====
  getUsers(params: any) {
    return request.get('/admin/users', { params })
  },
  createUser(data: any) {
    return request.post('/admin/users', data)
  },
  updateUser(id: number, data: any) {
    return request.put(`/admin/users/${id}`, data)
  },
  deleteUser(id: number) {
    return request.delete(`/admin/users/${id}`)
  },

  // ===== 学生管理 =====
  getStudents(params: any) {
    return request.get('/admin/students', { params })
  },
  createStudent(data: any) {
    return request.post('/admin/students', data)
  },
  updateStudent(id: number, data: any) {
    return request.put(`/admin/students/${id}`, data)
  },
  deleteStudent(id: number) {
    return request.delete(`/admin/students/${id}`)
  },

  // ===== 师生分配 =====
  getTeacherStudents(params: any) {
    return request.get('/admin/teacher-students', { params })
  },
  assignTeacherStudent(data: any) {
    return request.post('/admin/teacher-students', data)
  },
  removeTeacherStudent(id: number) {
    return request.delete(`/admin/teacher-students/${id}`)
  },

  // ===== 课程类型 =====
  getCourseTypes() {
    return request.get('/admin/course-types')
  },
  createCourseType(data: any) {
    return request.post('/admin/course-types', data)
  },
  updateCourseType(id: number, data: any) {
    return request.put(`/admin/course-types/${id}`, data)
  },
  deleteCourseType(id: number) {
    return request.delete(`/admin/course-types/${id}`)
  },

  // ===== 课时包 =====
  getPackages(params: any) {
    return request.get('/admin/packages', { params })
  },
  createPackage(data: any) {
    return request.post('/admin/packages', data)
  },
  updatePackage(id: number, data: any) {
    return request.put(`/admin/packages/${id}`, data)
  },
  deletePackage(id: number) {
    return request.delete(`/admin/packages/${id}`)
  },

  // ===== 上课记录 =====
  getRecords(params: any) {
    return request.get('/admin/records', { params })
  },
  createRecord(data: any) {
    return request.post('/admin/records', data)
  },
  updateRecord(id: number, data: any) {
    return request.put(`/admin/records/${id}`, data)
  },
  deleteRecord(id: number) {
    return request.delete(`/admin/records/${id}`)
  },
  exportRecords(params: any) {
    return request.get('/admin/records/export', { params, responseType: 'blob' })
  },
  approveRecord(id: number, comment: string = '') {
    return request.put(`/admin/records/${id}/approve`, null, { params: { comment } })
  },
  rejectRecord(id: number, comment: string = '') {
    return request.put(`/admin/records/${id}/reject`, null, { params: { comment } })
  },

  // ===== 统计 =====
  getStatisticsOverview() {
    return request.get('/admin/statistics/overview')
  },
  exportStatistics() {
    return request.get('/admin/statistics/export', { responseType: 'blob' })
  },
}
