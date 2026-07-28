/**
 * Axios 实例 + 请求/响应拦截器
 */
import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 Axios 实例
const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ---- 请求拦截器 ----
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token 并添加到请求头
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// ---- 响应拦截器 ----
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 成功响应直接返回
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response

      // 401 未授权：清除 token 并跳转登录页
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('role')
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
        return Promise.reject(error)
      }

      // 403 禁止访问
      if (status === 403) {
        ElMessage.error(typeof data?.detail === 'string' ? data.detail : '权限不足')
        return Promise.reject(error)
      }

      // 422 参数校验错误 — 字段级中文提示
      if (status === 422 && Array.isArray(data?.detail)) {
        const fieldNames: Record<string, string> = {
          username: '用户名', password: '密码', real_name: '真实姓名', role: '角色',
          phone: '手机号', email: '邮箱', name: '名称', admin_password: '管理员密码',
          student_id: '学生', course_type_id: '课程类型', parent_user_id: '家长',
          hours: '课时数', content: '上课内容', date: '上课时间',
        }
        const typeMsgs: Record<string, string> = {
          'string_too_short': '长度不足',
          'value_error.any_str.min_length': '长度不足',
          'greater_than': '必须大于0',
          'field required': '为必填项',
        }
        const msgs = data.detail.map((e: any) => {
          const field = e.loc?.slice(-1)[0] || ''
          const label = fieldNames[field] || field
          let msg = e.msg
          // 针对常见字段做友好提示
          if (field === 'password' || field === 'admin_password') msg = '要求至少6位'
          else if (e.type === 'string_too_short') msg = `要求至少${e.ctx?.min_length || '?'}个字符`
          else if (e.type === 'greater_than') msg = '必须大于0'
          else if (e.type === 'missing') msg = '为必填项'
          return `${label}${msg}`
        }).join('；')
        ElMessage.error(msgs)
        return Promise.reject(error)
      }

      // 其他错误
      const message = typeof data?.detail === 'string' ? data.detail : (data?.msg || '请求失败')
      ElMessage.error(message)
    } else {
      ElMessage.error('网络连接异常')
    }
    return Promise.reject(error)
  }
)

export default request
