<!--
  教师端-个人统计页面
-->
<template>
  <div class="page-container">
    <h3>个人统计</h3>
    <el-row :gutter="16" style="margin-top:20px">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover" style="text-align:center">
          <div style="font-size:28px;font-weight:bold" :style="{ color: card.color }">{{ card.value }}</div>
          <div style="color:#909399;margin-top:8px">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top:20px">
      <template #header>各状态记录占比</template>
      <div v-if="total > 0" style="display:flex;gap:24px;align-items:flex-end;height:200px;padding:20px">
        <div v-for="bar in bars" :key="bar.label" style="text-align:center;flex:1">
          <div :style="{ height: bar.height + 'px', background: bar.color, borderRadius: '4px 4px 0 0', minWidth: '60px' }"></div>
          <div style="margin-top:8px">{{ bar.label }}</div>
          <div style="font-weight:bold">{{ bar.count }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { teacherApi } from '@/api/teacher'

const stats = ref({ total_records: 0, pending_records: 0, approved_records: 0, rejected_records: 0, total_approved_hours: 0, student_count: 0 })

const cards = computed(() => [
  { label: '我的学生数', value: stats.value.student_count, color: '#409EFF' },
  { label: '总记录数', value: stats.value.total_records, color: '#909399' },
  { label: '已审核通过', value: stats.value.approved_records, color: '#67C23A' },
  { label: '通过课时合计', value: `${stats.value.total_approved_hours} h`, color: '#409EFF' },
])
const total = computed(() => stats.value.total_records || 1)
const bars = computed(() => [
  { label: '待审核', count: stats.value.pending_records, color: '#E6A23C', height: (stats.value.pending_records / total.value) * 150 },
  { label: '已通过', count: stats.value.approved_records, color: '#67C23A', height: (stats.value.approved_records / total.value) * 150 },
  { label: '已驳回', count: stats.value.rejected_records, color: '#F56C6C', height: (stats.value.rejected_records / total.value) * 150 },
])

onMounted(async () => {
  try {
    const res = await teacherApi.getMyStatistics()
    stats.value = res.data.data
  } catch { /* */ }
})
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
</style>
