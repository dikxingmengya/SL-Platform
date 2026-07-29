<!-- 管理端布局：响应式侧边栏 + 内容区 -->
<template>
  <el-container class="layout-container">
    <!-- 移动端遮罩 -->
    <div v-if="isMobile && !collapsed" class="mobile-overlay" @click="collapsed = true" />

    <!-- 左侧菜单 -->
    <el-aside :width="collapsed ? '0px' : '220px'" class="layout-aside" :class="{ 'aside-mobile': isMobile, 'aside-open': !collapsed }">
      <div class="logo">
        <h2>SL-Platform</h2>
        <p>管理后台</p>
      </div>
      <el-menu
        :default-active="activeMenu" router
        background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF"
        @select="onMenuSelect"
      >
        <el-menu-item index="/admin/dashboard"><el-icon><DataAnalysis /></el-icon><span>首页概览</span></el-menu-item>
        <el-menu-item index="/admin/users"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
        <el-menu-item index="/admin/students"><el-icon><School /></el-icon><span>学生管理</span></el-menu-item>
        <el-menu-item index="/admin/teacher-students"><el-icon><Connection /></el-icon><span>师生分配</span></el-menu-item>
        <el-menu-item index="/admin/course-types"><el-icon><Collection /></el-icon><span>课程类型</span></el-menu-item>
        <el-menu-item index="/admin/packages"><el-icon><ShoppingBag /></el-icon><span>课时包管理</span></el-menu-item>
        <el-menu-item index="/admin/records"><el-icon><Document /></el-icon><span>上课记录</span></el-menu-item>
        <el-menu-item index="/admin/statistics"><el-icon><TrendCharts /></el-icon><span>统计报表</span></el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-button text @click="collapsed = !collapsed" class="menu-toggle">
            <el-icon :size="20"><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
          </el-button>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item>管理端</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="user-name"><el-icon><UserFilled /></el-icon><span class="hide-mobile">{{ userStore.userInfo?.real_name }}</span></span>
          <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="layout-main"><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)
const isMobile = ref(false)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title as string || '')

function checkMobile() {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 768
  // 从移动端恢复到桌面端时自动展开侧边栏
  if (wasMobile && !isMobile.value) collapsed.value = false
}
function onMenuSelect() { if (isMobile.value) collapsed.value = true }
function handleLogout() { userStore.logout(); router.push('/login') }

// 刷新后恢复用户信息
userStore.fetchMe()

onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))
</script>

<style scoped>
.layout-container { height: 100vh; }
.layout-aside { background: #304156; overflow-y: auto; transition: width 0.3s; }
.aside-mobile { position: fixed; left: 0; top: 0; bottom: 0; z-index: 1000; width: 220px !important; }
.aside-mobile:not(.aside-open) { width: 0 !important; overflow: hidden; }
.mobile-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 999; }
.logo { padding: 16px; text-align: center; color: #fff; border-bottom: 1px solid rgba(255,255,255,.1); }
.logo h2 { margin: 0; font-size: 18px; }
.logo p { margin: 4px 0 0; font-size: 12px; color: #bfcbd9; }
.layout-header { background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between; padding: 0 12px; height: 56px; }
.header-left { display: flex; align-items: center; gap: 8px; }
.header-right { display: flex; align-items: center; gap: 8px; }
.user-name { display: flex; align-items: center; gap: 4px; }
.layout-main { background: #f0f2f5; min-height: calc(100vh - 56px); padding: 12px; }
.menu-toggle { display: none; }

@media (max-width: 767px) {
  .menu-toggle { display: inline-flex; }
  .hide-mobile { display: none; }
  .breadcrumb { display: none; }
  .layout-main { padding: 8px; }
}
</style>
