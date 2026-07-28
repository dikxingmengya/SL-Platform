<!--
  教师端首页：个人统计概览
-->
<template>
  <div class="page-container">
    <h3>欢迎，{{ userStore.userInfo?.real_name }}老师</h3>
    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover" style="text-align:center">
          <div style="font-size:28px;font-weight:bold;color:var(--el-color-primary)">{{ card.value }}</div>
          <div style="margin-top:8px;color:#909399">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { teacherApi } from '@/api/teacher'

const userStore = useUserStore()
const cards = ref([
  { label: '我的学生', value: 0 },
  { label: '总记录数', value: 0 },
  { label: '已审核通过课时', value: '0 h' },
  { label: '待审核记录', value: 0 },
])

onMounted(async () => {
  try {
    const res = await teacherApi.getMyStatistics()
    const d = res.data.data
    cards.value[0].value = d.student_count
    cards.value[1].value = d.total_records
    cards.value[2].value = `${d.total_approved_hours} h`
    cards.value[3].value = d.pending_records
  } catch { /* */ }
})
</script>
