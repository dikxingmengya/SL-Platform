<!--
  管理端首页：统计概览
-->
<template>
  <div class="dashboard">
    <h3>系统概览</h3>
    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" :body-style="{ padding: '20px' }">
          <div class="stat-card">
            <div class="stat-icon" :style="{ background: card.color }">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 月度趋势 -->
    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>按月上课统计（已审核）</template>
          <el-table :data="monthlyTrend" size="small" max-height="350">
            <el-table-column prop="month" label="月份" width="100" />
            <el-table-column prop="lesson_count" label="上课次数" />
            <el-table-column prop="total_hours" label="总课时(h)" />
            <el-table-column prop="teacher_count" label="授课教师数" />
            <el-table-column prop="student_count" label="上课学生数" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>按月收入统计</template>
          <el-table :data="revenueTrend" size="small" max-height="350">
            <el-table-column prop="month" label="月份" width="100" />
            <el-table-column prop="package_count" label="课时包数量" />
            <el-table-column prop="total_revenue" label="总收入(元)" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw } from 'vue'
import {
  User, School, ShoppingBag, Checked, Document, TrendCharts,
} from '@element-plus/icons-vue'
import { adminApi } from '@/api/admin'

const statCards = ref([
  { label: '学生总数', value: 0, icon: markRaw(School), color: '#409EFF' },
  { label: '教师总数', value: 0, icon: markRaw(User), color: '#67C23A' },
  { label: '家长总数', value: 0, icon: markRaw(User), color: '#E6A23C' },
  { label: '待审核记录', value: 0, icon: markRaw(Checked), color: '#F56C6C' },
  { label: '课时包总数', value: 0, icon: markRaw(ShoppingBag), color: '#909399' },
  { label: '总课时(h)', value: 0, icon: markRaw(Document), color: '#409EFF' },
  { label: '已消耗课时(h)', value: 0, icon: markRaw(TrendCharts), color: '#E6A23C' },
  { label: '剩余课时(h)', value: 0, icon: markRaw(TrendCharts), color: '#67C23A' },
])

const monthlyTrend = ref<any[]>([])
const revenueTrend = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await adminApi.getStatisticsOverview()
    const { overview, monthly_trend, revenue_trend } = res.data.data
    statCards.value[0].value = overview.total_students
    statCards.value[1].value = overview.total_teachers
    statCards.value[2].value = overview.total_parents
    statCards.value[3].value = overview.pending_records
    statCards.value[4].value = overview.total_packages
    statCards.value[5].value = overview.total_package_hours
    statCards.value[6].value = overview.total_used_hours
    statCards.value[7].value = overview.remaining_hours
    monthlyTrend.value = monthly_trend || []
    revenueTrend.value = revenue_trend || []
  } catch { /* 加载失败 */ }
})
</script>

<style scoped>
.dashboard h3 { margin-top: 0; }
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 56px; height: 56px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.stat-value { font-size: 24px; font-weight: bold; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
</style>
