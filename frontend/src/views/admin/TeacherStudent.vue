<!--
  管理端-师生分配页面：多对多关联管理
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>师生分配管理</h3>
      <el-button type="primary" @click="openAssignDialog">+ 分配师生</el-button>
    </div>

    <el-card>
      <el-table :data="assignmentList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="teacher_name" label="教师" width="100" />
        <el-table-column prop="teacher_phone" label="教师电话" width="130" />
        <el-table-column prop="teacher_subject" label="擅长科目" width="120" />
        <el-table-column prop="student_name" label="学生" width="100" />
        <el-table-column prop="student_grade" label="年级" width="80" />
        <el-table-column prop="parent_name" label="家长" width="100" />
        <el-table-column prop="assigned_at" label="分配时间" width="160" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleRemove(row)">取消分配</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="loadData"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <!-- 分配对话框 -->
    <el-dialog v-model="dialogVisible" title="分配师生" width="450px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="选择教师" prop="teacher_id">
          <el-select v-model="form.teacher_id" filterable placeholder="搜索教师" style="width: 100%">
            <el-option
              v-for="t in teacherList"
              :key="t.id"
              :label="`${t.real_name} (${t.subject || '未填写科目'})`"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择学生" prop="student_id">
          <el-select v-model="form.student_id" filterable placeholder="搜索学生" style="width: 100%">
            <el-option
              v-for="s in studentSelectList"
              :key="s.id"
              :label="`${s.name} (${s.grade})`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="assigning" @click="handleAssign">确定分配</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { adminApi } from '@/api/admin'

const loading = ref(false), assigning = ref(false), dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const assignmentList = ref<any[]>([])
const teacherList = ref<any[]>([])
const studentSelectList = ref<any[]>([])
const page = ref(1), pageSize = ref(20), total = ref(0)

const form = reactive({ teacher_id: null as number | null, student_id: null as number | null })
const rules: FormRules = {
  teacher_id: [{ required: true, message: '请选择教师', trigger: 'change' }],
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
}

async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getTeacherStudents({ page: page.value, page_size: pageSize.value })
    const d = res.data.data
    assignmentList.value = d.items
    total.value = d.total
  } finally { loading.value = false }
}

async function openAssignDialog() {
  const [tRes, sRes] = await Promise.all([
    adminApi.getUsers({ page: 1, page_size: 200, role: 'teacher' }),
    adminApi.getStudents({ page: 1, page_size: 200 }),
  ])
  teacherList.value = tRes.data.data.items
  studentSelectList.value = sRes.data.data.items
  form.teacher_id = null
  form.student_id = null
  dialogVisible.value = true
}

async function handleAssign() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  assigning.value = true
  try {
    await adminApi.assignTeacherStudent({
      teacher_id: form.teacher_id,
      student_id: form.student_id,
    })
    ElMessage.success('分配成功')
    dialogVisible.value = false
    loadData()
  } catch { /* */ }
  finally { assigning.value = false }
}

async function handleRemove(row: any) {
  await ElMessageBox.confirm(`确定取消该分配关系吗？`, '确认', { type: 'warning' })
  await adminApi.removeTeacherStudent(row.id)
  ElMessage.success('已取消分配')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h3 { margin: 0; }
</style>
