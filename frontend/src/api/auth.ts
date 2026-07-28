/**
 * 认证相关 API
 */
import request from './request'

export const authApi = {
  /** 登录 */
  login(username: string, password: string) {
    return request.post('/auth/login', { username, password })
  },
  /** 获取当前用户信息 */
  getMe() {
    return request.get('/auth/me')
  },
}
