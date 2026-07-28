/**
 * SL-Platform 前端入口
 * 注册 Vue 应用、Pinia 状态管理、Vue Router、Element Plus 组件库
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia 状态管理
const pinia = createPinia()
app.use(pinia)

// 路由
app.use(router)

// Element Plus（中文语言包）
app.use(ElementPlus, { locale: zhCn })

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
