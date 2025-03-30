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

    <el-row :gutter="20" class="mt-20"><!-- 使用Element UI的el-row组件，设置列间距为20，添加上边距 -->
      <el-col :span="8"><!-- 使用Element UI的el-col组件，设置列宽度为8 -->
        <el-card class="feature-card"><!-- 功能卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="feature-header">
              <el-icon><Document /></el-icon><!-- 图标 -->
              <span>水印处理</span><!-- 功能名称 -->
            </div>
          </template>
          <div class="feature-content">
            <p>支持多种水印算法，包括：</p><!-- 功能描述 -->
            <ul>
              <li>DIP (Dynamic Identity Projection)</li>
              <li>EWD (Entropy Watermarking)</li>
              <li>SIR (Statistical Incoherence)</li>
              <li>SynthID</li>
              <li>SemStamp</li>
            </ul>
            <el-button type="primary" @click="router.push('/watermark')"><!-- 跳转按钮 -->
              开始使用
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8"><!-- 使用Element UI的el-col组件，设置列宽度为8 -->
        <el-card class="feature-card"><!-- 功能卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="feature-header">
              <el-icon><DataAnalysis /></el-icon><!-- 图标 -->
              <span>评估分析</span><!-- 功能名称 -->
            </div>
          </template>
          <div class="feature-content">
            <p>全面的评估指标：</p><!-- 功能描述 -->
            <ul>
              <li>安全性评估</li>
              <li>鲁棒性评估</li>
              <li>文本质量评估</li>
              <li>攻击测试</li>
            </ul>
            <el-button type="primary" @click="router.push('/evaluate')"><!-- 跳转按钮 -->
              开始评估
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8"><!-- 使用Element UI的el-col组件，设置列宽度为8 -->
        <el-card class="feature-card"><!-- 功能卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="feature-header">
              <el-icon><Connection /></el-icon><!-- 图标 -->
              <span>API接口</span><!-- 功能名称 -->
            </div>
          </template>
          <div class="feature-content">
            <p>标准化API支持：</p><!-- 功能描述 -->
            <ul>
              <li>OpenAI格式兼容</li>
              <li>RESTful API设计</li>
              <li>完整的接口文档</li>
              <li>SDK支持</li>
            </ul>
            <el-button type="primary" @click="router.push('/profile')"><!-- 跳转按钮 -->
              管理API密钥
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <!-- 模型调用和数据集管理两个卡片 -->
    <el-row :gutter="20" class="mt-20" justify="center">
      <el-col :span="8"><!-- 使用Element UI的el-col组件，设置列宽度为8 -->
        <el-card class="feature-card"><!-- 功能卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="feature-header">
              <el-icon><Cpu /></el-icon><!-- 图标 -->
              <span>模型调用</span><!-- 功能名称 -->
            </div>
          </template>
          <div class="feature-content">
            <p>强大的模型管理功能：</p><!-- 功能描述 -->
            <ul>
              <li>多种模型支持</li>
              <li>批量处理能力</li>
              <li>模型性能监控</li>
              <li>自定义参数配置</li>
              <li>模型版本管理</li>
            </ul>
            <el-button type="primary" @click="router.push('/models')"><!-- 跳转按钮 -->
              调用模型
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8"><!-- 使用Element UI的el-col组件，设置列宽度为8 -->
        <el-card class="feature-card"><!-- 功能卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="feature-header">
              <el-icon><Collection /></el-icon><!-- 图标 -->
              <span>数据集管理</span><!-- 功能名称 -->
            </div>
          </template>
          <div class="feature-content">
            <p>完整的数据集工具：</p><!-- 功能描述 -->
            <ul>
              <li>数据集导入导出</li>
              <li>数据预处理</li>
              <li>数据可视化分析</li>
              <li>自动标注功能</li>
              <li>数据质量评估</li>
            </ul>
            <el-button type="primary" @click="router.push('/dataset')"><!-- 跳转按钮 -->
              管理数据集
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'; // 引入Vue Router的useRouter函数
import { Document, DataAnalysis, Connection, Cpu } from '@element-plus/icons-vue'; // 引入Element Plus的图标

const router = useRouter(); // 获取路由实例
</script>

<style scoped>
.home-container {
  padding: 20px; /* 设置容器内边距 */
}

.welcome-card {
  margin-bottom: 20px; /* 设置卡片底部外边距 */
}

.welcome-header {
  display: flex;
  align-items: center; /* 设置头部内容的对齐方式 */
}

.welcome-content {
  font-size: 16px; /* 设置内容字体大小 */
  line-height: 1.6; /* 设置内容行高 */
}

.mt-20 {
  margin-top: 20px; /* 设置上边距 */
}

.feature-card {
  height: 100%; /* 设置卡片高度 */
}

.feature-header {
  display: flex;
  align-items: center; /* 设置头部内容的对齐方式 */
  gap: 10px; /* 设置头部内容的间距 */
  font-size: 16px; /* 设置头部字体大小 */
}

.feature-content {
  text-align: left; /* 设置内容的对齐方式 */
}

.feature-content ul {
  margin: 15px 0; /* 设置列表的上下外边距 */
  padding-left: 20px; /* 设置列表的左内边距 */
}

.feature-content li {
  margin: 5px 0; /* 设置列表项的上下外边距 */
}

.el-button {
  width: 100%; /* 设置按钮宽度 */
  margin-top: 15px; /* 设置按钮上边距 */
}
</style>