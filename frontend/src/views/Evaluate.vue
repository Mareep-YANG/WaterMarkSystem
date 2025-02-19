<template>
  <div class="evaluate-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>性能评估</h3>
            </div>
          </template>

          <el-form :model="formData" label-position="top">
            <el-form-item label="原始文本">
              <el-input
                v-model="formData.originalText"
                type="textarea"
                :rows="4"
                placeholder="请输入原始文本"
              />
            </el-form-item>

            <el-form-item label="水印文本">
              <el-input
                v-model="formData.watermarkedText"
                type="textarea"
                :rows="4"
                placeholder="请输入带水印文本"
              />
            </el-form-item>

            <el-form-item label="水印算法">
              <el-select v-model="formData.algorithm" placeholder="选择算法">
                <el-option
                  v-for="algo in algorithms"
                  :key="algo.name"
                  :label="algo.name"
                  :value="algo.name"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="水印密钥">
              <el-input
                v-model="formData.key"
                placeholder="请输入水印密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="评估指标">
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

        <el-card class="mt-20">
          <template #header>
            <div class="card-header">
              <h3>攻击测试</h3>
            </div>
          </template>

          <el-form :model="attackData" label-position="top">
            <el-form-item label="攻击类型">
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

      <el-col :span="12">
        <el-card v-if="result.metrics">
          <template #header>
            <h3>评估结果</h3>
          </template>

          <div class="metrics-results">
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

            <div v-if="result.details" class="metrics-details mt-20">
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

        <el-card v-if="result.attack" class="mt-20">
          <template #header>
            <h3>攻击结果</h3>
          </template>

          <div class="attack-results">
            <el-alert
              :title="'攻击' + (result.attack.success_rate > 0.5 ? '成功' : '失败')"
              :type="result.attack.success_rate > 0.5 ? 'success' : 'error'"
              show-icon
            >
              成功率: {{ (result.attack.success_rate * 100).toFixed(2) }}%
            </el-alert>

            <div class="mt-20">
              <h4>攻击后的文本</h4>
              <el-input
                v-model="result.attack.attacked_text"
                type="textarea"
                :rows="4"
                readonly
              />
            </div>

            <div v-if="result.attack.details" class="attack-details mt-20">
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
import { reactive, computed } from 'vue';
import { useWatermarkStore } from '@/stores';
import { ElMessage } from 'element-plus';
import api from '@/api';

interface ResultState {
  metrics: {
    robustness?: number;
    quality?: number;
    security?: number;
  } | null;
  details: Record<string, any> | null;
  attack: {
    success_rate: number;
    attacked_text: string;
    details: Record<string, any>;
  } | null;
}

const watermarkStore = useWatermarkStore();

const algorithms = computed(() => watermarkStore.algorithms);

const formData = reactive({
  originalText: '',
  watermarkedText: '',
  algorithm: '',
  key: '',
  metrics: [] as string[],
});

const attackData = reactive({
  type: 'text',
});

const loading = reactive({
  evaluate: false,
  attack: false,
});

const result = reactive<ResultState>({
  metrics: null,
  details: null,
  attack: null,
});

const format = (percentage: number) => percentage.toFixed(2) + '%';

const handleEvaluate = async () => {
  if (!formData.originalText || !formData.watermarkedText || !formData.algorithm || !formData.key) {
    ElMessage.warning('请填写完整信息');
    return;
  }

  if (formData.metrics.length === 0) {
    ElMessage.warning('请选择至少一个评估指标');
    return;
  }

  try {
    loading.evaluate = true;
    const response = await api.evaluate.metrics({
      original_text: formData.originalText,
      watermarked_text: formData.watermarkedText,
      algorithm: formData.algorithm,
      key: formData.key,
      metrics: formData.metrics,
    });
    
    result.metrics = response.metrics;
    result.details = response.details;
    ElMessage.success('评估完成');
  } catch (error: any) {
    ElMessage.error(error.message || '评估失败');
  } finally {
    loading.evaluate = false;
  }
};

const handleAttack = async () => {
  if (!formData.watermarkedText || !formData.algorithm || !formData.key) {
    ElMessage.warning('请先进行水印评估');
    return;
  }

  try {
    loading.attack = true;
    const response = await api.evaluate.attack({
      text: formData.watermarkedText,
      algorithm: formData.algorithm,
      key: formData.key,
      attack_type: attackData.type,
    });
    
    result.attack = response;
    ElMessage.success('攻击测试完成');
  } catch (error: any) {
    ElMessage.error(error.message || '攻击测试失败');
  } finally {
    loading.attack = false;
  }
};
</script>

<style scoped>
.evaluate-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.full-width {
  width: 100%;
}

.mt-20 {
  margin-top: 20px;
}

.metrics-results,
.attack-results {
  .el-row {
    margin-bottom: 20px;
  }
}

.metrics-details,
.attack-details {
  border-top: 1px solid #dcdfe6;
  padding-top: 20px;
}
</style>