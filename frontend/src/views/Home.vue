<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="welcome-header">
              <h2>欢迎使用文本水印系统</h2>
            </div>
          </template>
          <div class="welcome-content">
            <p>本系统提供多种文本水印算法，支持水印嵌入、检测和评估功能。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="feature-header">
              <el-icon><Document /></el-icon>
              <span>水印处理</span>
            </div>
          </template>
          <div class="feature-content">
            <p>支持多种水印算法，包括：</p>
            <ul>
              <li>DIP (Dynamic Identity Projection)</li>
              <li>EWD (Entropy Watermarking)</li>
              <li>SIR (Statistical Incoherence)</li>
              <li>SynthID</li>
              <li>SemStamp</li>
            </ul>
            <el-button type="primary" @click="router.push('/watermark')">
              开始使用
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="feature-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>评估分析</span>
            </div>
          </template>
          <div class="feature-content">
            <p>全面的评估指标：</p>
            <ul>
              <li>安全性评估</li>
              <li>鲁棒性评估</li>
              <li>文本质量评估</li>
              <li>攻击测试</li>
            </ul>
            <el-button type="primary" @click="router.push('/evaluate')">
              开始评估
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="feature-header">
              <el-icon><Connection /></el-icon>
              <span>API接口</span>
            </div>
          </template>
          <div class="feature-content">
            <p>标准化API支持：</p>
            <ul>
              <li>OpenAI格式兼容</li>
              <li>RESTful API设计</li>
              <li>完整的接口文档</li>
              <li>SDK支持</li>
            </ul>
            <el-button type="primary" @click="router.push('/profile')">
              管理API密钥
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { Document, DataAnalysis, Connection } from '@element-plus/icons-vue';

const router = useRouter();
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-header {
  display: flex;
  align-items: center;
}

.welcome-content {
  font-size: 16px;
  line-height: 1.6;
}

.mt-20 {
  margin-top: 20px;
}

.feature-card {
  height: 100%;
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.feature-content {
  text-align: left;
}

.feature-content ul {
  margin: 15px 0;
  padding-left: 20px;
}

.feature-content li {
  margin: 5px 0;
}

.el-button {
  width: 100%;
  margin-top: 15px;
}
</style>