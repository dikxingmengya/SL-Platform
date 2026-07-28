<!--
  家长端-我的课时包明细页面
  课时包归属家长，名下所有孩子共享
-->
<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/parent/dashboard')">
      <template #content>
        <span style="font-size:18px;font-weight:bold">我的课时包</span>
      </template>
      <template #extra>
        <el-tag type="info">名下所有孩子共享</el-tag>
      </template>
    </el-page-header>

    <el-row :gutter="16" style="margin: 20px 0">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" style="text-align:center">
          <div style="font-size:24px;font-weight:bold;color:#409EFF">{{ totalPackages }}</div>
          <div style="color:#909399">课时包总数</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" style="text-align:center">
          <div style="font-size:24px;font-weight:bold;color:#67C23A">{{ totalRemaining.toFixed(1) }}</div>
          <div style="color:#909399">总剩余课时(h)</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" style="text-align:center">
          <div style="font-size:24px;font-weight:bold;color:#E6A23C">{{ totalUsed.toFixed(1) }}</div>
          <div style="color:#909399">已消耗课时(h)</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-table :data="packages" v-loading="loading" border stripe>
        <el-table-column prop="id" label="编号" width="60" />
        <el-table-column prop="course_type_name" label="课程类型" width="120" />
        <el-table-column prop="total_hours" label="总课时" width="100" />
        <el-table-column prop="used_hours" label="已消耗" width="100" />
        <el-table-column prop="remaining_hours" label="剩余课时" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.remaining_hours <= 0 ? '#F56C6C' : '#67C23A', fontWeight: 'bold' }">
              {{ row.remaining_hours.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="进度" min-width="150">
          <template #default="{ row }">
            <el-progress
              :percentage="row.total_hours > 0 ? Math.round((row.used_hours / row.total_hours) * 100) : 0"
              :color="progressColor(row)"
              :stroke-width="16"
            />
          </template>
        </el-table-column>
        <el-table-column prop="price" label="金额(元)" width="100" />
        <el-table-column prop="expire_date" label="有效期" width="110" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { parentApi } from '@/api/parent'

const loading = ref(false)
const packages = ref<any[]>([])

const totalPackages = computed(() => packages.value.length)
const totalRemaining = computed(() => packages.value.reduce((sum, p) => sum + p.remaining_hours, 0))
const totalUsed = computed(() => packages.value.reduce((sum, p) => sum + p.used_hours, 0))

function statusType(s: string) {
  return { active: 'success', expired: 'warning', depleted: 'danger' }[s] || 'info'
}
function statusLabel(s: string) {
  return { active: '有效', expired: '过期', depleted: '耗尽' }[s] || s
}
function progressColor(row: any) {
  const pct = row.total_hours > 0 ? (row.used_hours / row.total_hours) : 0
  if (pct >= 1) return '#F56C6C'
  if (pct >= 0.8) return '#E6A23C'
  return '#67C23A'
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await parentApi.getMyPackages()
    packages.value = res.data.data.packages
  } finally { loading.value = false }
})
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
</style>
