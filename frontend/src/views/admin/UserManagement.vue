<!--
  管理端-用户管理页面：管理员/教师/家长账号 CRUD
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>用户管理</h3>
      <el-button type="primary" @click="openDialog()">+ 创建用户</el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card style="margin-bottom: 16px">
      <el-form :inline="true">
        <el-form-item label="角色筛选">
          <el-select v-model="filterRole" placeholder="全部" clearable @change="loadData" style="width: 150px">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="家长" value="parent" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户表格 -->
    <el-card>
      <el-table :data="userList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_super_admin" type="danger" size="small">超级管理员</el-tag>
            <el-tag v-else :type="roleType(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="160" />
        <el-table-column prop="subject" label="擅长科目" width="120" />
        <el-table-column prop="is_active" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.is_super_admin">
              <el-tag type="danger" size="small">受保护</el-tag>
            </template>
            <template v-else>
              <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @change="loadData"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '创建用户'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" placeholder="密码（编辑时留空不修改）" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option v-if="userStore.userInfo?.is_super_admin" label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="家长" value="parent" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="手机号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <!-- 教师专用字段 -->
        <template v-if="form.role === 'teacher'">
          <el-form-item label="擅长科目">
            <el-input v-model="form.subject" placeholder="如：数学,物理" />
          </el-form-item>
          <el-form-item label="个人简介">
            <el-input v-model="form.bio" type="textarea" :rows="2" placeholder="教师简介" />
          </el-form-item>
        </template>
        <el-form-item label="启用状态" v-if="isEdit">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { adminApi } from '@/api/admin'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const userList = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterRole = ref('')
const editId = ref<number | null>(null)

const form = reactive({
  username: '', password: '', real_name: '', role: 'parent',
  phone: '', email: '', subject: '', bio: '', is_active: true,
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

function roleType(role: string) {
  return { admin: 'danger', teacher: 'warning', parent: 'success' }[role] || 'info'
}
function roleLabel(role: string) {
  return { admin: '管理员', teacher: '教师', parent: '家长' }[role] || role
}

async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterRole.value) params.role = filterRole.value
    const res = await adminApi.getUsers(params)
    const d = res.data.data
    userList.value = d.items
    total.value = d.total
  } finally { loading.value = false }
}

function openDialog(row?: any) {
  isEdit.value = !!row
  editId.value = row?.id || null
  if (row) {
    Object.assign(form, {
      username: row.username, password: '', real_name: row.real_name,
      role: row.role, phone: row.phone, email: row.email,
      subject: row.subject || '', bio: row.bio || '', is_active: row.is_active,
    })
  } else {
    Object.assign(form, {
      username: '', password: '', real_name: '', role: 'parent',
      phone: '', email: '', subject: '', bio: '', is_active: true,
    })
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  // 编辑用户且修改了密码，需二次验证管理员密码
  let adminPwd = ''
  if (isEdit.value && form.password) {
    try {
      const { value } = await ElMessageBox.prompt('请输入您的管理员密码以确认修改', '🔐 身份验证', {
        inputType: 'password', confirmButtonText: '确认', inputPlaceholder: '请输入当前管理员密码',
      })
      if (!value) { ElMessage.error('密码不能为空'); return }
      adminPwd = value
    } catch { return }
  }

  saving.value = true
  try {
    const payload: any = {
      real_name: form.real_name, phone: form.phone, email: form.email,
      subject: form.subject, bio: form.bio,
    }
    if (form.password) { payload.password = form.password; if (adminPwd) payload.admin_password = adminPwd }
    if (isEdit.value) {
      payload.is_active = form.is_active
      await adminApi.updateUser(editId.value!, payload)
      ElMessage.success('用户已更新')
    } else {
      Object.assign(payload, { username: form.username, role: form.role })
      if (!form.password) { ElMessage.error('请输入密码'); return }
      payload.password = form.password
      await adminApi.createUser(payload)
      ElMessage.success('用户已创建')
    }
    dialogVisible.value = false
    loadData()
  } catch { /* handled by interceptor */ }
  finally { saving.value = false }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定要删除用户「${row.real_name}」吗？`, '确认删除', { type: 'warning' })
  await adminApi.deleteUser(row.id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h3 { margin: 0; }
</style>
