<!--
  管理端-统计报表页面：概览 + 趋势 + Excel 导出
-->
<template>
  <div class="page-container">
    <div class="page-header">
      <h3>统计报表</h3>
      <el-button type="success" :loading="exporting" @click="handleExport">📥 导出Excel报表</el-button>
    </div>

    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :xs="24" :sm="12" :md="8" v-for="card in overviewCards" :key="card.label">
        <el-card shadow="hover" class="overview-card">
          <div class="oc-value" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="oc-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card><template #header>按月上课趋势</template>
          <el-table :data="monthlyTrend" size="small" max-height="400">
            <el-table-column prop="month" label="月份" width="100" />
            <el-table-column prop="lesson_count" label="上课次数" />
            <el-table-column prop="total_hours" label="总课时(h)" />
            <el-table-column prop="teacher_count" label="教师数" />
            <el-table-column prop="student_count" label="学生数" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card><template #header>按月收入趋势</template>
          <el-table :data="revenueTrend" size="small" max-height="400">
            <el-table-column prop="month" label="月份" width="100" />
            <el-table-column prop="package_count" label="课时包数量" />
            <el-table-column prop="total_revenue" label="收入(元)" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/admin'

const exporting = ref(false)
const monthlyTrend = ref<any[]>([])
const revenueTrend = ref<any[]>([])

const overviewCards = ref([
  { label: '学生总数', value: 0, color: '#409EFF' },
  { label: '教师总数', value: 0, color: '#67C23A' },
  { label: '待审核记录', value: 0, color: '#F56C6C' },
  { label: '课时包总收入(元)', value: '0.00', color: '#409EFF' },
  { label: '已消耗课时(h)', value: 0, color: '#E6A23C' },
  { label: '剩余课时(h)', value: 0, color: '#67C23A' },
])

onMounted(async () => {
  try {
    const res = await adminApi.getStatisticsOverview()
    const { overview, monthly_trend, revenue_trend } = res.data.data
    overviewCards.value[0].value = overview.total_students
    overviewCards.value[1].value = overview.total_teachers
    overviewCards.value[2].value = overview.pending_records
    overviewCards.value[3].value = overview.total_package_revenue?.toFixed(2) || '0.00'
    overviewCards.value[4].value = overview.total_used_hours
    overviewCards.value[5].value = overview.remaining_hours
    monthlyTrend.value = monthly_trend || []
    revenueTrend.value = revenue_trend || []
  } catch { /* */ }
})

async function handleExport() {
  exporting.value = true
  try {
    const res = await adminApi.exportStatistics()
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'SL-Platform-统计报表.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } finally { exporting.value = false }
}
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h3 { margin: 0; }
.overview-card { text-align: center; }
.oc-value { font-size: 28px; font-weight: bold; }
.oc-label { font-size: 13px; color: #909399; margin-top: 8px; }
</style>
