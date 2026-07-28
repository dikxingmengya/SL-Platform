<!--
  教师端-我的学生列表：卡片展示，含家长联系电话
-->
<template>
  <div class="page-container">
    <h3>我的学生（{{ studentList.length }}人）</h3>
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" v-for="s in studentList" :key="s.student_id" style="margin-bottom:16px">
        <el-card shadow="hover">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-weight:bold;font-size:16px">{{ s.student_name }}</span>
              <el-tag size="small">{{ s.student_grade }}</el-tag>
            </div>
          </template>
          <div class="card-info">
            <div class="info-item">
              <span class="label">学校：</span><span>{{ s.school || '未填写' }}</span>
            </div>
            <div class="info-item">
              <span class="label">家长：</span><span>{{ s.parent_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">联系电话：</span>
              <span style="color:#409EFF;font-weight:bold">{{ s.parent_phone || '未填写' }}</span>
            </div>
            <div class="info-item">
              <span class="label">分配时间：</span><span>{{ s.assigned_at || '-' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="studentList.length === 0" :span="24">
        <el-empty description="暂无分配的学生，请联系管理员进行师生分配" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { teacherApi } from '@/api/teacher'

const studentList = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await teacherApi.getMyStudents()
    studentList.value = res.data.data
  } catch { /* */ }
})
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
.card-info { display: flex; flex-direction: column; gap: 8px; }
.info-item .label { color: #909399; font-size: 13px; }
</style>
