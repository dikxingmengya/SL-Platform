<!-- 管理端-上课记录管理：筛选 + 编辑/删除/审核 -->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>上课记录</h3>
      <div>
        <el-button type="primary" @click="openCreate">创建记录</el-button>
        <el-button type="success" :loading="exporting" @click="handleExport">导出Excel</el-button>
      </div>
    </div>

    <!-- 筛选 -->
    <el-card style="margin-bottom:16px">
      <el-form :inline="true" size="small">
        <el-form-item label="状态">
          <el-select v-model="filterStatus" clearable @change="loadData" style="width:100px">
            <el-option value="">全部</el-option>
            <el-option value="draft" label="草稿"/>
            <el-option value="pending" label="待审核"/>
            <el-option value="approved" label="已通过"/>
            <el-option value="rejected" label="已驳回"/>
          </el-select>
        </el-form-item>
        <el-form-item label="教师">
          <el-select v-model="filterTeacher" filterable clearable @change="loadData" style="width:130px">
            <el-option v-for="t in teachers" :key="t.id" :label="t.real_name" :value="t.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="学生">
          <el-select v-model="filterStudent" filterable clearable @change="loadData" style="width:130px">
            <el-option v-for="s in allStudents" :key="s.id" :label="s.name" :value="s.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="家长">
          <el-select v-model="filterParent" filterable clearable @change="loadData" style="width:130px">
            <el-option v-for="p in parents" :key="p.id" :label="p.real_name" :value="p.id"/>
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="recordList" v-loading="loading" border stripe size="small">
        <el-table-column prop="id" label="ID" width="45" />
        <el-table-column prop="student_name" label="学生" width="70" />
        <el-table-column prop="parent_name" label="家长" width="70" />
        <el-table-column prop="teacher_name" label="教师" width="70" />
        <el-table-column prop="course_type_name" label="课程" width="70" />
        <el-table-column prop="hours" label="课时" width="55" />
        <el-table-column prop="date" label="时间" width="140" />
        <el-table-column prop="content" label="内容" min-width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right" align="center">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(cmd: string) => handleCommand(cmd, row)" placement="bottom-end">
              <el-button size="small" class="op-dropdown-btn">
                操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">
                    <el-icon><Edit /></el-icon> 编辑
                  </el-dropdown-item>
                  <template v-if="row.status==='pending'">
                    <el-dropdown-item command="approve" class="dropdown-success">
                      <el-icon><Select /></el-icon> 通过
                    </el-dropdown-item>
                    <el-dropdown-item command="reject" class="dropdown-warning">
                      <el-icon><CloseBold /></el-icon> 驳回
                    </el-dropdown-item>
                  </template>
                  <el-dropdown-item command="delete" class="dropdown-danger" divided>
                    <el-icon><Delete /></el-icon> 删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="loadData"
        style="margin-top:16px;justify-content:flex-end"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑上课记录" width="520px">
      <el-form ref="editFormRef" :model="ef" :rules="erules" label-width="90px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="ef.student_id" filterable placeholder="选择学生">
            <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.parent_name})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型" prop="course_type_id">
          <el-select v-model="ef.course_type_id" placeholder="选择课程">
            <el-option label="通用" :value="null" />
            <el-option v-for="c in courseTypes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课时间" prop="date">
          <el-date-picker v-model="ef.date" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="课时" prop="hours">
          <el-input-number v-model="ef.hours" :min="0.5" :step="0.5" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="ef.content" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 创建记录对话框 -->
    <el-dialog v-model="createVisible" title="创建上课记录" width="520px">
      <el-form ref="createFormRef" :model="cf" :rules="crules" label-width="90px">
        <el-form-item label="学生" prop="student_id">
          <el-select v-model="cf.student_id" filterable placeholder="选择学生">
            <el-option v-for="s in allStudents" :key="s.id" :label="`${s.name} (${s.parent_name})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教师" prop="teacher_id">
          <el-select v-model="cf.teacher_id" filterable placeholder="选择教师">
            <el-option v-for="t in teachers" :key="t.id" :label="t.real_name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型" prop="course_type_id">
          <el-select v-model="cf.course_type_id" placeholder="选择课程">
            <el-option label="通用" :value="null" />
            <el-option v-for="c in courseTypes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课时间" prop="date">
          <el-date-picker v-model="cf.date" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
        </el-form-item>
        <el-form-item label="课时" prop="hours">
          <el-input-number v-model="cf.hours" :min="0.5" :step="0.5" style="width:100%" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="cf.content" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateSave">创建并提交</el-button>
        <el-button :loading="creating" @click="handleCreateDraft">存为草稿</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { adminApi } from '@/api/admin'

const loading = ref(false), saving = ref(false), creating = ref(false), exporting = ref(false)
const editVisible = ref(false), createVisible = ref(false)
const editFormRef = ref<FormInstance>(), createFormRef = ref<FormInstance>()
const recordList = ref<any[]>([])
const students = ref<any[]>([])     // 编辑用
const allStudents = ref<any[]>([])  // 筛选下拉
const teachers = ref<any[]>([])     // 筛选下拉
const parents = ref<any[]>([])      // 筛选下拉
const courseTypes = ref<any[]>([])
const page = ref(1), pageSize = ref(20), total = ref(0)
const filterStatus = ref(''), filterTeacher = ref(''), filterStudent = ref(''), filterParent = ref('')
const editId = ref<number | null>(null)

const ef = reactive({ student_id: null as number | null, course_type_id: null as number | null, date: '', hours: 2, content: '' })
const cf = reactive({ student_id: null as number | null, teacher_id: null as number | null, course_type_id: null as number | null, date: '', hours: 2, content: '' })
const erules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_type_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  date: [{ required: true, message: '请选择时间', trigger: 'change' }],
  hours: [{ required: true, message: '请输入课时', trigger: 'blur' }],
}
const crules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  teacher_id: [{ required: true, message: '请选择教师', trigger: 'change' }],
  course_type_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  date: [{ required: true, message: '请选择时间', trigger: 'change' }],
  hours: [{ required: true, message: '请输入课时', trigger: 'blur' }],
}

function statusType(s: string) { return { draft:'info', pending:'warning', approved:'success', rejected:'danger' }[s]||'info' }
function statusLabel(s: string) { return { draft:'草稿', pending:'待审核', approved:'已通过', rejected:'已驳回' }[s]||s }

function handleCommand(cmd: string, row: any) {
  if (cmd === 'edit') openEdit(row)
  else if (cmd === 'approve') handleApprove(row)
  else if (cmd === 'reject') handleReject(row)
  else if (cmd === 'delete') handleDelete(row)
}

function buildParams() {
  const p: any = { page: page.value, page_size: pageSize.value }
  if (filterStatus.value) p.status = filterStatus.value
  if (filterTeacher.value) p.teacher_id = filterTeacher.value
  if (filterStudent.value) p.student_id = filterStudent.value
  if (filterParent.value) p.parent_user_id = filterParent.value
  return p
}
async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getRecords(buildParams())
    const d = res.data.data; recordList.value = d.items; total.value = d.total
  } finally { loading.value = false }
}
async function handleExport() {
  exporting.value = true
  try {
    const res = await adminApi.exportRecords(buildParams())
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
    // 构建文件名：上课记录_筛选条件_时间戳
    const parts = ['上课记录']
    if (filterStatus.value) {
      const m: Record<string,string> = { draft:'草稿', pending:'待审核', approved:'已通过', rejected:'已驳回' }
      parts.push(m[filterStatus.value] || filterStatus.value)
    }
    if (filterTeacher.value) {
      const t = teachers.value.find((x: any) => x.id == filterTeacher.value)
      if (t) parts.push('教师' + t.real_name)
    }
    if (filterStudent.value) {
      const s = allStudents.value.find((x: any) => x.id == filterStudent.value)
      if (s) parts.push(s.name)
    }
    if (filterParent.value) {
      const p = parents.value.find((x: any) => x.id == filterParent.value)
      if (p) parts.push('家长' + p.real_name)
    }
    const ts = new Date().toISOString().replace(/[-:T]/g,'').slice(0,14)
    parts.push(ts)
    a.download = parts.join('_') + '.xlsx'
    a.click(); URL.revokeObjectURL(a.href)
    ElMessage.success('导出成功')
  } finally { exporting.value = false }
}

async function openEdit(row: any) {
  editId.value = row.id
  ef.student_id = row.student_id; ef.course_type_id = row.course_type_id
  ef.date = row.date; ef.hours = row.hours; ef.content = row.content
  const [sRes, cRes] = await Promise.all([adminApi.getStudents({ page:1,page_size:500 }), adminApi.getCourseTypes()])
  students.value = sRes.data.data.items; courseTypes.value = cRes.data.data
  editVisible.value = true
}

async function handleEditSave() {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try { await adminApi.updateRecord(editId.value!, ef); ElMessage.success('已更新'); editVisible.value = false; loadData() }
  finally { saving.value = false }
}

async function handleApprove(row: any) {
  try {
    const { value: comment } = await ElMessageBox.prompt('审核意见（可选）', '通过审核', { confirmButtonText:'确认通过', inputType:'textarea', inputPlaceholder:'可填写备注...' })
    await adminApi.approveRecord(row.id, comment||'')
    ElMessage.success('审核通过，课时已自动扣减'); loadData()
  } catch { /* 取消 */ }
}

async function handleReject(row: any) {
  try {
    const { value: comment } = await ElMessageBox.prompt('驳回原因', '驳回', { confirmButtonText:'确认驳回', inputType:'textarea', inputPlaceholder:'请填写原因...' })
    await adminApi.rejectRecord(row.id, comment||''); ElMessage.success('已驳回'); loadData()
  } catch { /* 取消 */ }
}

async function handleDelete(row: any) {
  const isApproved = row.status === 'approved'
  const msg = isApproved
    ? `<p style="color:#F56C6C;font-size:15px">此记录已审核通过，已扣减 <b>${row.hours}</b> 课时。</p><p>删除后将<b>自动退回</b>已扣课时到家长课时包中。</p><p>确定删除？</p>`
    : '确定删除该上课记录吗？'
  try {
    await ElMessageBox.confirm(msg, isApproved ? '⚠️ 删除已审核记录' : '确认删除', {
      type: isApproved ? 'error' : 'warning',
      confirmButtonText: isApproved ? '确认删除并退课时' : '确认删除',
      dangerouslyUseHTMLString: isApproved,
    })
  } catch { return }
  const res = await adminApi.deleteRecord(row.id)
  ElMessage.success(res.data.msg)
  loadData()
}

async function openCreate() {
  cf.student_id = null; cf.teacher_id = null; cf.course_type_id = null
  cf.date = ''; cf.hours = 2; cf.content = ''
  createVisible.value = true
}

async function saveRecord(status: string) {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  creating.value = true
  try {
    await adminApi.createRecord({ ...cf, status })
    ElMessage.success(status === 'draft' ? '草稿已保存' : '记录已创建')
    createVisible.value = false
    loadData()
  } finally { creating.value = false }
}
function handleCreateSave() { saveRecord('pending') }
function handleCreateDraft() { saveRecord('draft') }

onMounted(async () => {
  const [tRes, sRes, pRes] = await Promise.all([
    adminApi.getUsers({ page_size: 500, role: 'teacher' }),
    adminApi.getStudents({ page_size: 500 }),
    adminApi.getUsers({ page_size: 500, role: 'parent' }),
  ])
  teachers.value = tRes.data.data.items
  allStudents.value = sRes.data.data.items
  parents.value = pRes.data.data.items
  loadData()
})
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h3 { margin: 0; }
.op-dropdown-btn { border: 1px solid #dcdfe6; border-radius: 4px; padding: 5px 10px; }
.dropdown-success { color: #67C23A !important; }
.dropdown-warning { color: #E6A23C !important; }
.dropdown-danger { color: #F56C6C !important; }
</style>
