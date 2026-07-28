/**
 * 用户状态管理 (Pinia Store)
 * 管理 token、用户信息、角色
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export interface UserInfo {
  id: number
  username: string
  real_name: string
  role: string
  is_super_admin: boolean
  phone: string
  email: string
  is_active: boolean
}

export const useUserStore = defineStore('user', () => {
  // ---- 状态 ----
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  // ---- 计算属性 ----
  const role = computed(() => userInfo.value?.role || '')
  const isLoggedIn = computed(() => !!token.value)

  // ---- 方法 ----
  /**
   * 登录
   */
  async function login(username: string, password: string) {
    const res = await authApi.login(username, password)
    const data = res.data.data
    token.value = data.token
    userInfo.value = {
      id: data.user_id,
      username: data.username,
      real_name: data.real_name,
      role: data.role,
      phone: '',
      email: '',
      is_active: true,
    }
    localStorage.setItem('token', data.token)
    localStorage.setItem('role', data.role)
    return data
  }

  /**
   * 获取当前用户信息
   */
  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await authApi.getMe()
      userInfo.value = res.data.data
    } catch {
      logout()
    }
  }

  /**
   * 退出登录
   */
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
  }

  /**
   * 从 localStorage 恢复状态
   */
  function restoreFromStorage() {
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      token.value = savedToken
    }
  }

  return {
    token,
    userInfo,
    role,
    isLoggedIn,
    login,
    fetchMe,
    logout,
    restoreFromStorage,
  }
})
