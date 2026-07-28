<!--
  登录页面
  支持三种角色登录：管理员/教师/家长
-->
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>📚 SL-Platform</h1>
        <p>家教课时管理系统</p>
      </div>

      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        label-position="top"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/**
 * 处理登录
 * 登录成功后根据角色跳转到对应首页
 */
async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const data = await userStore.login(loginForm.username, loginForm.password)
    ElMessage.success(`欢迎回来，${data.real_name}！`)

    // 根据角色跳转
    const roleMap: Record<string, string> = {
      admin: '/admin/dashboard',
      teacher: '/teacher/dashboard',
      parent: '/parent/dashboard',
    }
    router.push(roleMap[data.role] || '/')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '登录失败，请检查用户名密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  border: 1px solid #ebeef5;
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-header h1 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}
.login-header p {
  margin: 8px 0 0;
  color: #909399;
  font-size: 14px;
}
</style>
