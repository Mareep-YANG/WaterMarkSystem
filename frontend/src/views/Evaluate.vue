<template>
  <div class="evaluate-container"><!-- 评估页面的容器 -->
    <el-row :gutter="20"><!-- 使用Element UI的el-row组件，设置列间距为20 -->
      <el-col :span="12"><!-- 使用Element UI的el-col组件，设置列宽度为12 -->
        <el-card><!-- 评估卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="card-header">
              <h3>性能评估</h3><!-- 性能评估标题 -->
            </div>
          </template>

          <el-form :model="formData" label-position="top"><!-- 表单区域 -->
            <el-form-item label="原始文本"><!-- 原始文本输入区域 -->
              <el-input
                v-model="formData.originalText"
                type="textarea"
                :rows="4"
                placeholder="请输入原始文本"
              />
            </el-form-item>

            <el-form-item label="水印文本"><!-- 水印文本输入区域 -->
              <el-input
                v-model="formData.watermarkedText"
                type="textarea"
                :rows="4"
                placeholder="请输入带水印文本"
              />
            </el-form-item>

            <el-form-item label="水印算法"><!-- 水印算法选择区域 -->
              <el-select v-model="formData.algorithm" placeholder="选择算法">
                <el-option
                  v-for="algo in algorithms"
                  :key="algo.name"
                  :label="algo.name"
                  :value="algo.name"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="水印密钥"><!-- 水印密钥输入区域 -->
              <el-input
                v-model="formData.key"
                placeholder="请输入水印密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="评估指标"><!-- 评估指标选择区域 -->
              <el-checkbox-group v-model="formData.metrics">
                <el-checkbox label="robustness">鲁棒性</el-checkbox>
                <el-checkbox label="quality">文本质量</el-checkbox>
                <el-checkbox label="security">安全性</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-button
              type="primary"
              :loading="loading.evaluate"
              @click="handleEvaluate"
              class="full-width"
            >
              开始评估
            </el-button>
          </el-form>
        </el-card>

        <el-card class="mt-20"><!-- 攻击测试卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="card-header">
              <h3>攻击测试</h3><!-- 攻击测试标题 -->
            </div>
          </template>

          <el-form :model="attackData" label-position="top"><!-- 表单区域 -->
            <el-form-item label="攻击类型"><!-- 攻击类型选择区域 -->
              <el-select v-model="attackData.type" placeholder="选择攻击类型">
                <el-option label="文本攻击" value="text" />
                <el-option label="语义攻击" value="semantic" />
                <el-option label="Logits攻击" value="logits" />
              </el-select>
            </el-form-item>

            <el-button
              type="warning"
              :loading="loading.attack"
              @click="handleAttack"
              class="full-width"
            >
              执行攻击
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12"><!-- 使用Element UI的el-col组件，设置列宽度为12 -->
        <el-card v-if="result.metrics"><!-- 评估结果卡片 -->
          <template #header>
            <h3>评估结果</h3><!-- 评估结果标题 -->
          </template>

          <div class="metrics-results"><!-- 评估结果内容区域 -->
            <el-row v-if="result.metrics.robustness !== undefined">
              <el-col :span="12">鲁棒性评分：</el-col>
              <el-col :span="12">
                <el-progress
                  :percentage="result.metrics.robustness * 100"
                  :format="format"
                />
              </el-col>
            </el-row>

            <el-row v-if="result.metrics.quality !== undefined">
              <el-col :span="12">文本质量评分：</el-col>
              <el-col :span="12">
                <el-progress
                  :percentage="result.metrics.quality * 100"
                  :format="format"
                />
              </el-col>
            </el-row>

            <el-row v-if="result.metrics.security !== undefined">
              <el-col :span="12">安全性评分：</el-col>
              <el-col :span="12">
                <el-progress
                  :percentage="result.metrics.security * 100"
                  :format="format"
                />
              </el-col>
            </el-row>

            <div v-if="result.details" class="metrics-details mt-20"><!-- 详细信息区域 -->
              <h4>详细信息</h4>
              <el-descriptions border>
                <el-descriptions-item
                  v-for="(value, key) in result.details"
                  :key="key"
                  :label="key"
                >
                  {{ JSON.stringify(value) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>

        <el-card v-if="result.attack" class="mt-20"><!-- 攻击结果卡片 -->
          <template #header>
            <h3>攻击结果</h3><!-- 攻击结果标题 -->
          </template>

          <div class="attack-results"><!-- 攻击结果内容区域 -->
            <el-alert
              :title="'攻击' + (result.attack.success_rate > 0.5 ? '成功' : '失败')"
              :type="result.attack.success_rate > 0.5 ? 'success' : 'error'"
              show-icon
            >
              成功率: {{ (result.attack.success_rate * 100).toFixed(2) }}%
            </el-alert>

            <div class="mt-20">
              <h4>攻击后的文本</h4><!-- 攻击后的文本区域 -->
              <el-input
                v-model="result.attack.attacked_text"
                type="textarea"
                :rows="4"
                readonly
              />
            </div>

            <div v-if="result.attack.details" class="attack-details mt-20"><!-- 详细信息区域 -->
              <h4>详细信息</h4>
              <el-descriptions border>
                <el-descriptions-item
                  v-for="(value, key) in result.attack.details"
                  :key="key"
                  :label="key"
                >
                  {{ JSON.stringify(value) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'; // 引入Vue的相关函数
import { useWatermarkStore } from '@/stores'; // 引入水印存储
import { ElMessage } from 'element-plus'; // 引入Element Plus的消息组件
import api from '@/api'; // 引入API模块

interface ResultState {
  metrics: {
    robustness?: number; // 鲁棒性评分
    quality?: number; // 文本质量评分
    security?: number; // 安全性评分
  } | null;
  details: Record<string, any> | null; // 详细信息
  attack: {
    success_rate: number; // 攻击成功率
    attacked_text: string; // 攻击后的文本
    details: Record<string, any>; // 攻击详细信息
  } | null;
}

const watermarkStore = useWatermarkStore(); // 获取水印存储实例

const algorithms = computed(() => watermarkStore.algorithms); // 计算属性，获取水印算法列表

const formData = reactive({
  originalText: '', // 原始文本
  watermarkedText: '', // 水印文本
  algorithm: '', // 水印算法
  key: '', // 水印密钥
  metrics: [] as string[], // 评估指标
});

const attackData = reactive({
  type: 'text', // 攻击类型
});

const loading = reactive({
  evaluate: false, // 评估加载状态
  attack: false, // 攻击加载状态
});

const result = reactive<ResultState>({
  metrics: null, // 评估结果
  details: null, // 详细信息
  attack: null, // 攻击结果
});

const format = (percentage: number) => percentage.toFixed(2) + '%'; // 格式化百分比

const handleEvaluate = async () => {// 定义一个异步函数 handleEvaluate，用于处理水印评估的逻辑
  if (!formData.originalText || !formData.watermarkedText || !formData.algorithm || !formData.key) {// 检查表单数据是否完整，包括原始文本、水印文本、算法和密钥
    ElMessage.warning('请填写完整信息');// 如果信息不完整，显示警告消息
    return;
  }

  if (formData.metrics.length === 0) { // 检查是否选择了至少一个评估指标
    ElMessage.warning('请选择至少一个评估指标');// 如果没有选择评估指标，显示警告消息
    return;
  }

  try {
    loading.evaluate = true;// 开始评估，设置加载状态为true
    const response = await api.evaluate.metrics({// 调用API进行水印评估，传入必要的参数
      original_text: formData.originalText,// 原始文本
      watermarked_text: formData.watermarkedText,// 水印文本
      algorithm: formData.algorithm,// 使用的算法
      key: formData.key, // 密钥
      metrics: formData.metrics,// 评估指标
    });
    
    result.metrics = response.metrics;
    result.details = response.details;// 将评估结果和详细信息保存到结果对象中
    ElMessage.success('评估完成');// 显示成功消息
  } catch (error: any) {
    ElMessage.error(error.message || '评估失败'); // 如果发生错误，显示错误消息
  } finally {
    loading.evaluate = false;// 无论成功或失败，最后都将加载状态设置为false
  }
};

const handleAttack = async () => {// 定义一个异步函数 handleAttack，用于处理攻击测试的逻辑
  if (!formData.watermarkedText || !formData.algorithm || !formData.key) {// 检查水印文本、算法和密钥是否已填写
    ElMessage.warning('请先进行水印评估');// 如果未填写，显示警告消息
    return;
  }

  try {
    loading.attack = true;// 开始攻击测试，设置加载状态为true
    const response = await api.evaluate.attack({// 调用API进行攻击测试，传入必要的参数
      text: formData.watermarkedText, // 水印文本
      algorithm: formData.algorithm,// 使用的算法
      key: formData.key,// 密钥
      attack_type: attackData.type,// 攻击类型
    });
    
    result.attack = response;// 将攻击测试结果保存到结果对象中
    ElMessage.success('攻击测试完成');// 显示成功消息
  } catch (error: any) {
    ElMessage.error(error.message || '攻击测试失败');// 如果发生错误，显示错误消息
  } finally {
    loading.attack = false;// 无论成功或失败，最后都将加载状态设置为false
  }
};
</script>

<style scoped>
.evaluate-container {
  padding: 20px; /* 设置容器内边距 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* 设置头部内容的对齐方式 */
}

.full-width {
  width: 100%; /* 设置全宽 */
}

.mt-20 {
  margin-top: 20px; /* 设置上边距 */
}

.metrics-results,
.attack-results {
  .el-row {
    margin-bottom: 20px; /* 设置行的下边距 */
  }
}

.metrics-details,
.attack-details {
  border-top: 1px solid #dcdfe6; /* 设置详细信息区域的上边框 */
  padding-top: 20px; /* 设置详细信息区域的上内边距 */
}
</style>