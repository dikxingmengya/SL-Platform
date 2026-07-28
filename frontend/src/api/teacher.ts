/**
 * 教师端 API
 */
import request from './request'

export const teacherApi = {
  /** 我的学生列表 */
  getMyStudents() {
    return request.get('/teacher/students')
  },
  /** 创建上课记录 */
  createRecord(data: any) {
    return request.post('/teacher/records', data)
  },
  /** 我的上课记录 */
  getMyRecords(params: any) {
    return request.get('/teacher/records', { params })
  },
  /** 获取课程类型列表 */
  getCourseTypes() {
    return request.get('/teacher/course-types')
  },
  /** 编辑草稿 */
  updateDraft(id: number, data: any) {
    return request.put(`/teacher/records/${id}`, data)
  },
  /** 提交草稿 */
  submitDraft(id: number) {
    return request.put(`/teacher/records/${id}/submit`)
  },
  /** 个人统计 */
  getMyStatistics() {
    return request.get('/teacher/statistics')
  },
}
