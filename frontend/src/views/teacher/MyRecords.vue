<!--
  教师端-我的上课记录：分页 + 状态筛选
-->
<template>
  <div class="page-container">
    <h3>我的上课记录</h3>
    <el-card style="margin-top:16px">
      <el-form :inline="true">
        <el-form-item label="状态筛选">
          <el-select v-model="filterStatus" clearable @change="loadData" style="width:140px">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="草稿" value="draft" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-table :data="recordList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="student_name" label="学生" width="100" />
        <el-table-column prop="course_type_name" label="课程" width="90" />
        <el-table-column prop="hours" label="课时" width="70" />
        <el-table-column prop="date" label="上课时间" width="155" />
        <el-table-column prop="content" label="内容" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_comment" label="审核意见" width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'draft'">
              <el-button type="warning" size="small" @click="openEdit(row)">编辑</el-button>
              <el-button type="primary" size="small" @click="handleSubmitDraft(row)">提交</el-button>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160" />
      </el-table>
      <el-pagination
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="loadData"
        style="margin-top:16px;justify-content:flex-end"
      />
    </el-card>

    <!-- 编辑草稿对话框 -->
    <el-dialog v-model="editVisible" title="编辑草稿" width="520px">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
        <el-form-item label="选择学生" prop="student_id">
          <el-select v-model="editForm.student_id" filterable placeholder="选择学生" style="width:100%">
            <el-option v-for="s in studentList" :key="s.student_id" :label="`${s.student_name}`" :value="s.student_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型" prop="course_type_id">
          <el-select v-model="editForm.course_type_id" placeholder="选择课程" style="width:100%">
            <el-option v-for="c in courseTypes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课时间" prop="date">
          <el-date-picker v-model="editForm.date" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DD HH:mm:ss" :disabled-date="disabledDate" style="width:100%" />
        </el-form-item>
        <el-form-item label="课时数" prop="hours">
          <el-input-number v-model="editForm.hours" :min="0.5" :step="0.5" style="width:100%" />
        </el-form-item>
        <el-form-item label="上课内容">
          <el-input v-model="editForm.content" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { teacherApi } from '@/api/teacher'

const loading = ref(false), saving = ref(false), editVisible = ref(false)
const editFormRef = ref<FormInstance>()
const recordList = ref<any[]>([])
const studentList = ref<any[]>([])
const courseTypes = ref<any[]>([])
const page = ref(1), pageSize = ref(20), total = ref(0)
const filterStatus = ref('')
const editId = ref<number | null>(null)
const editForm = reactive({
  student_id: null as number | null,
  course_type_id: null as number | null,
  date: '',
  hours: 2,
  content: '',
})
const editRules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_type_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  date: [{ required: true, message: '请选择时间', trigger: 'change' }],
  hours: [{ required: true, message: '请输入课时', trigger: 'blur' }],
}

function disabledDate(time: Date) { return time.getTime() > Date.now() }

function statusType(s: string) {
  return { draft: 'info', pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info'
}
function statusLabel(s: string) {
  return { draft: '草稿', pending: '待审核', approved: '已通过', rejected: '已驳回' }[s] || s
}

async function openEdit(row: any) {
  editId.value = row.id
  editForm.student_id = row.student_id
  editForm.course_type_id = row.course_type_id
  editForm.date = row.date
  editForm.hours = row.hours
  editForm.content = row.content
  // 加载下拉数据
  const [sRes, ctRes] = await Promise.all([
    teacherApi.getMyStudents(),
    teacherApi.getCourseTypes(),
  ])
  studentList.value = sRes.data.data
  courseTypes.value = ctRes.data.data.filter((c: any) => c.is_active)
  editVisible.value = true
}

async function handleEditSave() {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await teacherApi.updateDraft(editId.value!, editForm)
    ElMessage.success('草稿已更新')
    editVisible.value = false
    loadData()
  } finally { saving.value = false }
}

async function handleSubmitDraft(row: any) {
  await teacherApi.submitDraft(row.id)
  ElMessage.success('草稿已提交审核')
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filterStatus.value) params.status = filterStatus.value
    const res = await teacherApi.getMyRecords(params)
    const d = res.data.data
    recordList.value = d.items
    total.value = d.total
  } finally { loading.value = false }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
</style>
