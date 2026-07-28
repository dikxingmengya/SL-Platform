<!--
  家长端-孩子上课记录历史页面
-->
<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/parent/dashboard')">
      <template #content>
        <span style="font-size:18px;font-weight:bold">{{ studentName }} - 上课记录</span>
      </template>
    </el-page-header>

    <el-card style="margin-top:20px">
      <el-table :data="recordList" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="teacher_name" label="授课教师" width="100" />
        <el-table-column prop="course_type_name" label="课程" width="100" />
        <el-table-column prop="hours" label="课时" width="70" />
        <el-table-column prop="date" label="上课时间" width="155" />
        <el-table-column prop="content" label="内容" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewer_name" label="审核人" width="100" />
        <el-table-column prop="review_comment" label="审核意见" width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="提交时间" width="160" />
      </el-table>
      <el-pagination
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @change="loadData"
        style="margin-top:16px;justify-content:flex-end"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { parentApi } from '@/api/parent'

const route = useRoute()
const loading = ref(false)
const studentName = ref('')
const recordList = ref<any[]>([])
const page = ref(1), pageSize = ref(20), total = ref(0)

function statusType(s: string) {
  return { pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info'
}
function statusLabel(s: string) {
  return { pending: '待审核', approved: '已通过', rejected: '已驳回' }[s] || s
}

async function loadData() {
  loading.value = true
  try {
    const studentId = Number(route.params.id)
    const res = await parentApi.getChildRecords(studentId, { page: page.value, page_size: pageSize.value })
    const d = res.data.data
    // 从第一个记录中提取学生姓名
    if (d.items.length > 0 && !studentName.value) {
      studentName.value = d.items[0].student_name
    }
    recordList.value = d.items
    total.value = d.total
  } finally { loading.value = false }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
</style>
