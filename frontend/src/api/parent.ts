/**
 * 家长端 API
 */
import request from './request'

export const parentApi = {
  /** 我的孩子列表 */
  getChildren() {
    return request.get('/parent/children')
  },
  /** 我的课时包明细（家长级别，孩子共享） */
  getMyPackages() {
    return request.get('/parent/packages')
  },
  /** 某孩子的上课记录 */
  getChildRecords(studentId: number, params: any) {
    return request.get(`/parent/children/${studentId}/records`, { params })
  },
  /** 某孩子分配的教师 */
  getChildTeachers(studentId: number) {
    return request.get(`/parent/children/${studentId}/teachers`)
  },
  /** 我的通知 */
  getNotifications(params: any) {
    return request.get('/parent/notifications', { params })
  },
}
