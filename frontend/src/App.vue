<!--
  SL-Platform 根组件
  通过 <router-view /> 渲染对应页面
-->
<template>
  <router-view />
</template>

<script setup lang="ts">
// 根组件：仅作为路由容器
</script>

<style>
html, body, #app {
  margin: 0; padding: 0; height: 100%;
  font-family: 'Microsoft YaHei', '微软雅黑', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

/* ---- 移动端全局适配 ---- */
@media (max-width: 767px) {
  /* 表格横向滚动 */
  .el-table { display: block; overflow-x: auto; white-space: nowrap; }
  /* 对话框全屏 */
  .el-dialog { width: 95% !important; margin: 10px auto !important; }
  .el-dialog__body { padding: 12px !important; }
  /* 表单控件全宽 */
  .el-form-item .el-select,
  .el-form-item .el-date-picker,
  .el-form-item .el-input-number,
  .el-form-item .el-cascader,
  .el-form-item .el-input { width: 100% !important; }
  /* 内联表单移动端竖向排列 */
  .el-form--inline .el-form-item { display: block !important; margin-right: 0 !important; }
  .el-form--inline .el-form-item .el-select,
  .el-form--inline .el-form-item .el-input { width: 100% !important; }
  /* 卡片间距 */
  .el-card { margin-bottom: 8px; }
  /* 分页居中 */
  .el-pagination { justify-content: center !important; }
  /* 页头竖向排列 */
  .page-header { flex-direction: column !important; align-items: flex-start !important; gap: 10px !important; }
  .page-header h3 { margin-bottom: 0 !important; }
  .page-header .el-button { width: 100%; }
  /* 表格操作列按钮 */
  .el-table .el-button--small { margin: 2px 0; }
  /* 日期选择器面板不溢出 */
  .el-picker-panel { max-width: 95vw; left: 2.5vw !important; }
  /* 面包屑隐藏节省空间 */
  .el-breadcrumb { display: none !important; }
}
</style>
