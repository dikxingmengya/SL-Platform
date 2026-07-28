<!--
  家长端-孩子分配的教师页面
-->
<template>
  <div class="page-container">
    <el-page-header @back="$router.push('/parent/dashboard')">
      <template #content>
        <span style="font-size:18px;font-weight:bold">{{ studentName }} - 授课教师</span>
      </template>
    </el-page-header>

    <el-row :gutter="16" style="margin-top:20px">
      <el-col :xs="24" :sm="12" :md="8" v-for="t in teachers" :key="t.teacher_id" style="margin-bottom:16px">
        <el-card shadow="hover">
          <template #header>
            <div style="display:flex;align-items:center;gap:8px">
              <el-avatar :size="32" style="background:#409EFF">{{ t.teacher_name?.charAt(0) }}</el-avatar>
              <span style="font-weight:bold">{{ t.teacher_name }}</span>
            </div>
          </template>
          <div class="teacher-info">
            <div><span class="label">联系电话：</span>{{ t.teacher_phone || '未填写' }}</div>
            <div><span class="label">擅长科目：</span>{{ t.teacher_subject || '未填写' }}</div>
            <div><span class="label">分配时间：</span>{{ t.assigned_at || '-' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="teachers.length === 0" :span="24">
        <el-empty description="该学生暂未分配教师" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { parentApi } from '@/api/parent'

const route = useRoute()
const studentName = ref('')
const teachers = ref<any[]>([])

onMounted(async () => {
  try {
    const studentId = Number(route.params.id)
    const res = await parentApi.getChildTeachers(studentId)
    studentName.value = res.data.data.student?.name || ''
    teachers.value = res.data.data.teachers || []
  } catch { /* */ }
})
</script>

<style scoped>
.page-container { background: #fff; padding: 20px; border-radius: 8px; }
.teacher-info { display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
.teacher-info .label { color: #909399; }
</style>
