<template>
  <div class="home-container"><!-- 首页容器 -->
    <el-row :gutter="20"><!-- 使用Element UI的el-row组件，设置列间距为20 -->
      <el-col :span="24"><!-- 使用Element UI的el-col组件，设置列宽度为24 -->
        <el-card class="welcome-card"><!-- 欢迎卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="welcome-header">
              <h2>欢迎使用文本水印系统</h2><!-- 欢迎标题 -->
            </div>
          </template>
          <div class="welcome-content">
            <p>本系统提供多种文本水印算法，支持水印嵌入、检测和评估功能。</p><!-- 欢迎内容 -->
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="24">
        <SystemOverview />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import SystemOverview from '@/components/SystemOverview.vue'
</script>

<style scoped>
.home-container {
  padding: 20px; /* 设置容器内边距 */
}

.welcome-card {
  margin-bottom: 20px; /* 设置卡片底部外边距 */
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
}

.welcome-header {
  display: flex;
  align-items: center; /* 设置头部内容的对齐方式 */
}

.welcome-header h2 {
  color: var(--el-text-color-primary);
  margin: 0;
}

.welcome-content {
  font-size: 16px; /* 设置内容字体大小 */
  line-height: 1.6; /* 设置内容行高 */
  color: var(--el-text-color-regular);
}
</style>