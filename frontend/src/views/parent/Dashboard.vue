<!--
  家长端首页：课时总览 + 通知提醒 + 孩子列表
-->
<template>
  <div>
    <!-- 课时总览卡片 -->
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color:#67C23A">{{ overview.remaining.toFixed(1) }} h</div>
          <div class="stat-label">总剩余课时</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color:#E6A23C">{{ overview.used.toFixed(1) }} h</div>
          <div class="stat-label">已消耗课时</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color:#409EFF">{{ overview.total.toFixed(1) }} h</div>
          <div class="stat-label">总购买课时</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color:#909399">{{ overview.packageCount }}</div>
          <div class="stat-label">课时包数量</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div style="margin-top:16px;display:flex;gap:12px">
      <el-button type="primary" @click="$router.push('/parent/packages')">
        <el-icon><ShoppingBag /></el-icon> 查看所有课时包
      </el-button>
    </div>

    <h3 style="margin-top:24px">我的孩子（{{ children.length }}人）</h3>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :sm="12" :md="8" v-for="child in children" :key="child.id" style="margin-bottom: 16px">
        <el-card shadow="hover" class="child-card">
          <div class="child-avatar">
            <el-avatar :size="60" style="background: #409EFF; font-size: 24px">
              {{ child.name.charAt(0) }}
            </el-avatar>
          </div>
          <div class="child-info">
            <div class="child-name">{{ child.name }}</div>
            <div class="child-grade">{{ child.grade || '未填写年级' }}</div>
            <div class="child-school">{{ child.school || '未填写学校' }}</div>
          </div>
          <div class="child-actions">
            <el-button size="small" @click="goToRecords(child)">上课记录</el-button>
            <el-button size="small" @click="goToTeachers(child)">授课教师</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="children.length === 0" :span="24">
        <el-empty description="暂无绑定的孩子信息，请联系管理员创建学生档案" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingBag } from '@element-plus/icons-vue'
import { parentApi } from '@/api/parent'

const router = useRouter()
const children = ref<any[]>([])

const overview = reactive({ remaining: 0, used: 0, total: 0, packageCount: 0 })

onMounted(async () => {
  try {
    const [childRes, pkgRes] = await Promise.all([
      parentApi.getChildren(),
      parentApi.getMyPackages(),
    ])
    children.value = childRes.data.data
    const pkgs = pkgRes.data.data.packages || []
    overview.total = pkgs.reduce((s: number, p: any) => s + p.total_hours, 0)
    overview.used = pkgs.reduce((s: number, p: any) => s + p.used_hours, 0)
    overview.remaining = pkgs.reduce((s: number, p: any) => s + p.remaining_hours, 0)
    overview.packageCount = pkgs.length
  } catch { /* */ }
})

function goToRecords(child: any) {
  router.push(`/parent/children/${child.id}/records`)
}
function goToTeachers(child: any) {
  router.push(`/parent/children/${child.id}/teachers`)
}
</script>

<style scoped>
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: bold; }
.stat-label { font-size: 13px; color: #909399; margin-top: 6px; }
.child-card { transition: transform 0.2s; }
.child-card:hover { transform: translateY(-4px); }
.child-avatar { text-align: center; margin-bottom: 12px; }
.child-info { text-align: center; margin-bottom: 12px; }
.child-name { font-size: 18px; font-weight: bold; color: #303133; }
.child-grade { font-size: 13px; color: #909399; margin-top: 4px; }
.child-school { font-size: 12px; color: #C0C4CC; }
.child-actions { display: flex; gap: 8px; justify-content: center; }
</style>
