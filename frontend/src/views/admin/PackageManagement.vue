<!--
  管理端-课时包管理页面：购买课时包（归属家长） + 手动调整
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>课时包管理</h3>
      <el-button type="primary" @click="openBuyDialog">+ 购买课时包</el-button>
    </div>
    <el-card>
      <el-table :data="packageList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="parent_name" label="家长" width="100" />
        <el-table-column prop="course_type_name" label="课程类型" width="110">
          <template #default="{ row }">
            <el-tag :type="row.course_type_name ? '' : 'success'">{{ row.course_type_name || '通用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_hours" label="总课时" width="80" />
        <el-table-column prop="used_hours" label="已消耗" width="80" />
        <el-table-column prop="remaining_hours" label="剩余" width="80">
          <template #default="{ row }">
            <span :style="{ color: row.remaining_hours <= 0 ? '#F56C6C' : '#67C23A' }">
              {{ row.remaining_hours }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="金额(元)" width="100" />
        <el-table-column prop="expire_date" label="有效期" width="110" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="购买时间" width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEditDialog(row)">调整</el-button>
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

    <!-- 购买对话框 -->
    <el-dialog v-model="buyVisible" title="购买课时包（归属家长，孩子共享）" width="480px">
      <el-form ref="buyFormRef" :model="buyForm" :rules="buyRules" label-width="100px">
        <el-form-item label="选择家长" prop="parent_user_id">
          <el-select v-model="buyForm.parent_user_id" filterable placeholder="搜索家长" style="width:100%">
            <el-option v-for="p in parentList" :key="p.id" :label="`${p.real_name} (${p.phone})`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型">
          <el-select v-model="buyForm.course_type_id" placeholder="选择课程（不选=通用）" clearable style="width:100%">
            <el-option label="通用课时（不限课程）" :value="null" />
            <el-option v-for="c in courseTypeList" :key="c.id" :label="`${c.name} (${c.default_hourly_rate}元/h)`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课时数" prop="total_hours">
          <el-input-number v-model="buyForm.total_hours" :min="0.5" :step="0.5" style="width:100%" />
        </el-form-item>
        <el-form-item label="购买金额">
          <el-input-number v-model="buyForm.price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="有效期">
          <el-date-picker v-model="buyForm.expire_date" type="date" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="buyForm.notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="buyVisible = false">取消</el-button>
        <el-button type="primary" :loading="buying" @click="handleBuy">确认购买</el-button>
      </template>
    </el-dialog>

    <!-- 手动调整对话框 -->
    <el-dialog v-model="editVisible" title="手动调整课时包" width="450px">
      <el-form ref="editFormRef" :model="editForm" label-width="100px">
        <el-form-item label="总课时">
          <el-input-number v-model="editForm.total_hours" :min="0.5" style="width:100%" />
        </el-form-item>
        <el-form-item label="已消耗">
          <el-input-number v-model="editForm.used_hours" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="editForm.price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width:100%">
            <el-option label="有效" value="active" />
            <el-option label="过期" value="expired" />
            <el-option label="耗尽" value="depleted" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleEditSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { adminApi } from '@/api/admin'

const loading = ref(false), buying = ref(false), saving = ref(false)
const buyVisible = ref(false), editVisible = ref(false)
const buyFormRef = ref<FormInstance>(), editFormRef = ref<FormInstance>()
const packageList = ref<any[]>([])
const parentList = ref<any[]>([])
const courseTypeList = ref<any[]>([])
const page = ref(1), pageSize = ref(20), total = ref(0)
const editId = ref<number | null>(null)

const buyForm = reactive({
  parent_user_id: null as number | null, course_type_id: null as number | null,
  total_hours: 10, price: 0, expire_date: null as string | null, notes: '',
})
const buyRules: FormRules = {
  parent_user_id: [{ required: true, message: '请选择家长', trigger: 'change' }],
  course_type_id: [{ required: true, message: '请选择课程类型', trigger: 'change' }],
  total_hours: [{ required: true, message: '请输入课时数', trigger: 'blur' }],
}

const editForm = reactive({ total_hours: 0, used_hours: 0, price: 0, status: 'active' })

function statusType(s: string) {
  return { active: 'success', expired: 'warning', depleted: 'danger' }[s] || 'info'
}
function statusLabel(s: string) {
  return { active: '有效', expired: '过期', depleted: '耗尽' }[s] || s
}

async function loadData() {
  loading.value = true
  try {
    const res = await adminApi.getPackages({ page: page.value, page_size: pageSize.value })
    const d = res.data.data
    packageList.value = d.items
    total.value = d.total
  } finally { loading.value = false }
}

async function openBuyDialog() {
  const [pRes, cRes] = await Promise.all([
    adminApi.getUsers({ page: 1, page_size: 200, role: 'parent' }),
    adminApi.getCourseTypes(),
  ])
  parentList.value = pRes.data.data.items
  courseTypeList.value = cRes.data.data.filter((c: any) => c.is_active)
  Object.assign(buyForm, { parent_user_id: null, course_type_id: null, total_hours: 10, price: 0, expire_date: null, notes: '' })
  buyVisible.value = true
}

async function handleBuy() {
  const valid = await buyFormRef.value?.validate().catch(() => false)
  if (!valid) return
  buying.value = true
  try {
    await adminApi.createPackage({
      parent_user_id: buyForm.parent_user_id,
      course_type_id: buyForm.course_type_id,
      total_hours: buyForm.total_hours,
      price: buyForm.price,
      expire_date: buyForm.expire_date || undefined,
      notes: buyForm.notes,
    })
    ElMessage.success('课时包购买成功')
    buyVisible.value = false
    loadData()
  } finally { buying.value = false }
}

function openEditDialog(row: any) {
  editId.value = row.id
  Object.assign(editForm, {
    total_hours: row.total_hours,
    used_hours: row.used_hours,
    price: row.price,
    status: row.status,
  })
  editVisible.value = true
}

async function handleEditSave() {
  saving.value = true
  try {
    await adminApi.updatePackage(editId.value!, editForm)
    ElMessage.success('课时包已调整')
    editVisible.value = false
    loadData()
  } finally { saving.value = false }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定删除该课时包吗？此操作不可恢复。', '确认删除', { type: 'warning' })
  } catch { return }
  await adminApi.deletePackage(row.id)
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
