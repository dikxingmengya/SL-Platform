<!--
  管理端-学生档案管理页面：CRUD 含所属家长列
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>学生档案管理</h3>
      <el-button type="primary" @click="openDialog()">+ 创建学生</el-button>
    </div>

    <el-card>
      <el-table :data="studentList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="学生姓名" width="120" />
        <el-table-column prop="grade" label="年级" width="100" />
        <el-table-column prop="parent_name" label="所属家长" width="100" />
        <el-table-column prop="parent_phone" label="家长电话" width="130" />
        <el-table-column prop="school" label="学校" min-width="140" />
        <el-table-column prop="is_active" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '在读' : '停课' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="loadData"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学生' : '创建学生档案'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="学生姓名" prop="name">
          <el-input v-model="form.name" placeholder="学生姓名" />
        </el-form-item>
        <el-form-item label="所属家长" prop="parent_user_id">
          <el-select v-model="form.parent_user_id" filterable placeholder="选择家长" style="width: 100%">
            <el-option
              v-for="p in parentList"
              :key="p.id"
              :label="`${p.real_name} (${p.phone})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-input v-model="form.grade" placeholder="如：初二" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="form.school" placeholder="所在学校" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="在读状态" v-if="isEdit">
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
const studentList = ref<any[]>([])
const parentList = ref<any[]>([])
const page = ref(1), pageSize = ref(20), total = ref(0), editId = ref<number | null>(null)

const form = reactive({
  name: '', parent_user_id: null as number | null, grade: '', school: '', notes: '', is_active: true,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入学生姓名', trigger: 'blur' }],
  parent_user_id: [{ required: true, message: '请选择所属家长', trigger: 'change' }],
}

async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getStudents({ page: page.value, page_size: pageSize.value })
    const d = res.data.data
    studentList.value = d.items
    total.value = d.total
  } finally { loading.value = false }
}

async function loadParents() {
  const res = await adminApi.getUsers({ page: 1, page_size: 100, role: 'parent' })
  parentList.value = res.data.data.items
}

function openDialog(row?: any) {
  isEdit.value = !!row
  editId.value = row?.id || null
  if (row) {
    Object.assign(form, {
      name: row.name, parent_user_id: row.parent_user_id,
      grade: row.grade, school: row.school, notes: row.notes, is_active: row.is_active,
    })
  } else {
    Object.assign(form, { name: '', parent_user_id: null, grade: '', school: '', notes: '', is_active: true })
  }
  loadParents()
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload: any = {
      name: form.name, parent_user_id: form.parent_user_id,
      grade: form.grade, school: form.school, notes: form.notes,
    }
    if (isEdit.value) {
      payload.is_active = form.is_active
      await adminApi.updateStudent(editId.value!, payload)
      ElMessage.success('学生档案已更新')
    } else {
      await adminApi.createStudent(payload)
      ElMessage.success('学生档案已创建')
    }
    dialogVisible.value = false
    loadData()
  } catch { /* intercept */ }
  finally { saving.value = false }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定要删除「${row.name}」的档案吗？`, '确认', { type: 'warning' })
  await adminApi.deleteStudent(row.id)
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
