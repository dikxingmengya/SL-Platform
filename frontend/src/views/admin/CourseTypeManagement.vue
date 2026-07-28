<!--
  管理端-课程类型管理页面
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>课程类型管理</h3>
      <el-button type="primary" @click="openDialog()">+ 新增课程</el-button>
    </div>
    <el-card>
      <el-table :data="typeList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="课程名称" width="120" />
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column prop="default_hourly_rate" label="默认课时费(元/h)" width="150" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程类型' : '新增课程类型'" width="450px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="form.name" placeholder="如：数学" />
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input v-model="form.description" placeholder="简短描述" />
        </el-form-item>
        <el-form-item label="默认课时费">
          <el-input-number v-model="form.default_hourly_rate" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="是否启用" v-if="isEdit">
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

const loading = ref(false), saving = ref(false), dialogVisible = ref(false), isEdit = ref(false)
const formRef = ref<FormInstance>()
const typeList = ref<any[]>([])
const editId = ref<number | null>(null)

const form = reactive({ name: '', description: '', default_hourly_rate: 0, is_active: true })
const rules: FormRules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
}

async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getCourseTypes()
    typeList.value = res.data.data
  } finally { loading.value = false }
}

function openDialog(row?: any) {
  isEdit.value = !!row
  editId.value = row?.id || null
  if (row) {
    Object.assign(form, { name: row.name, description: row.description, default_hourly_rate: row.default_hourly_rate, is_active: row.is_active })
  } else {
    Object.assign(form, { name: '', description: '', default_hourly_rate: 0, is_active: true })
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = { name: form.name, description: form.description, default_hourly_rate: form.default_hourly_rate }
    if (isEdit.value) {
      await adminApi.updateCourseType(editId.value!, { ...payload, is_active: form.is_active })
      ElMessage.success('已更新')
    } else {
      await adminApi.createCourseType(payload)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该课程类型？', '确认', { type: 'warning' })
  await adminApi.deleteCourseType(row.id)
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
