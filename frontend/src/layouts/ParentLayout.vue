<!--
  家长端布局：顶部导航 + 内容区
-->
<template>
  <el-container class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="layout-header">
      <div class="header-left">
        <h2>📚 家教课时管理</h2>
      </div>
      <div class="header-center">
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          router
          background-color="transparent"
          class="nav-menu"
        >
          <el-menu-item index="/parent/dashboard">
            <el-icon><User /></el-icon>
            <span>我的孩子</span>
          </el-menu-item>
        </el-menu>
      </div>
      <div class="header-right">
        <span class="user-name">
          <el-icon><UserFilled /></el-icon>
          {{ userStore.userInfo?.real_name || '家长' }}
        </span>
        <el-tag type="success" size="small">家长</el-tag>
        <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </el-header>

    <!-- 内容区 -->
    <el-main class="layout-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => {
  // 匹配到 dashboard 或子路径
  if (route.path.startsWith('/parent/dashboard')) return '/parent/dashboard'
  return route.path
})

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container { height: 100vh; display: flex; flex-direction: column; }
.layout-header {
  background: #fff;
  border-bottom: 2px solid #409EFF;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  flex-shrink: 0;
}
.header-left h2 { margin: 0; font-size: 18px; color: #303133; }
.header-center { flex: 1; display: flex; justify-content: center; }
.nav-menu { border-bottom: none !important; }
.header-right { display: flex; align-items: center; gap: 12px; }
.user-name { display: flex; align-items: center; gap: 4px; }
.layout-main { background: #f0f2f5; flex: 1; padding: 24px; overflow-y: auto; }
</style>
