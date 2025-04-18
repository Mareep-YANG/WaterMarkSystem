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
            <el-form-item label="数据集">
              <el-select v-model="formData.dataset_id" placeholder="选择数据集">
                <el-option
                  v-for="dataset in datasets"
                  :key="dataset.id"
                  :label="dataset.name"
                  :value="dataset.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="水印算法"><!-- 水印算法选择区域 -->
              <el-select v-model="formData.algorithm" placeholder="选择算法">
                <el-option
                  v-for="algo in algorithms"
                  :key="algo.name"
                  :label="algo.name"
                  :value="algo.name"
                >
                  <el-tooltip
                    :content="algo.description"
                    placement="right"
                    effect="light"
                  >
                    <span>{{ algo.name }}</span>
                  </el-tooltip>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="水印参数" v-if="currentAlgorithmParams">
              <template v-for="(value, key) in currentAlgorithmParams" :key="key">
                <el-form-item :label="key">
                  <el-input-number
                    v-if="typeof value === 'number'"
                    v-model="formData.watermark_params[key]"
                    :min="0"
                    :step="0.1"
                  />
                  <el-input
                    v-else
                    v-model="formData.watermark_params[key]"
                  />
                </el-form-item>
              </template>
            </el-form-item>

            <el-form-item label="评估指标">
              <el-checkbox-group v-model="formData.metrics">
                <el-checkbox label="quality">文本质量</el-checkbox>
                <el-checkbox label="robustness">鲁棒性</el-checkbox>
                <el-checkbox label="detectability">可检测性</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="质量指标" v-if="formData.metrics.includes('quality')">
              <el-checkbox-group v-model="formData.quality_metrics">
                <el-checkbox label="PPL">困惑度</el-checkbox>
                <el-checkbox label="Log Diversity">对数多样性</el-checkbox>
                <el-checkbox label="BLEU">BLEU分数</el-checkbox>
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

        <el-card class="mt-20" v-if="formData.metrics.includes('robustness')"><!-- 攻击测试卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="card-header">
              <h3>攻击测试</h3><!-- 攻击测试标题 -->
            </div>
          </template>

          <el-form :model="attackData" label-position="top"><!-- 表单区域 -->
            <el-form-item label="攻击算法">
              <el-select v-model="attackData.type" placeholder="选择攻击算法">
                <el-option
                  v-for="attacker in attackers"
                  :key="attacker.name"
                  :label="attacker.name"
                  :value="attacker.name"
                >
                  <el-tooltip
                    :content="attacker.description"
                    placement="right"
                    effect="light"
                  >
                    <span>{{ attacker.name }}</span>
                  </el-tooltip>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="攻击参数" v-if="currentAttackerParams">
              <template v-for="(value, key) in currentAttackerParams" :key="key">
                <el-form-item :label="key">
                  <el-input-number
                    v-if="typeof value === 'number'"
                    v-model="attackData.params[key]"
                    :min="0"
                    :step="0.1"
                  />
                  <el-input
                    v-else
                    v-model="attackData.params[key]"
                  />
                </el-form-item>
              </template>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12"><!-- 使用Element UI的el-col组件，设置列宽度为12 -->
        <el-card v-if="currentTaskId">
          <template #header>
            <div class="card-header">
              <h3>任务状态</h3>
              <el-button
                type="danger"
                size="small"
                @click="cancelTask"
                :disabled="taskStatus === 'completed' || taskStatus === 'failed'"
              >
                取消任务
              </el-button>
            </div>
          </template>
          
          <div class="task-status">
            <el-steps :active="getStepActive" finish-status="success">
              <el-step title="等待中" :description="taskStatus === 'pending' ? '任务已创建' : ''" />
              <el-step title="处理中" :description="taskStatus === 'processing' ? '正在处理...' : ''" />
              <el-step title="完成" :description="taskStatus === 'completed' ? '任务已完成' : ''" />
            </el-steps>
            
            <div v-if="taskError" class="task-error">
              <el-alert
                :title="taskError"
                type="error"
                :closable="false"
              />
            </div>
          </div>
        </el-card>

        <el-card v-if="result.metrics"><!-- 评估结果卡片 -->
          <template #header>
            <h3>评估结果</h3><!-- 评估结果标题 -->
          </template>

          <div class="metrics-results"><!-- 评估结果内容区域 -->
            <!-- 文本质量指标 -->
            <template v-if="result.metrics?.quality">
              <el-row>
                <el-col :span="24">
                  <h4>文本质量指标</h4>
                </el-col>
              </el-row>
              <el-row v-if="result.metrics.quality.PPL !== undefined">
                <el-col :span="12">困惑度 (PPL)：</el-col>
                <el-col :span="12">{{ result.metrics.quality.PPL?.toFixed(2) }}</el-col>
              </el-row>
              <el-row v-if="result.metrics.quality['Log Diversity'] !== undefined">
                <el-col :span="12">对数多样性：</el-col>
                <el-col :span="12">{{ result.metrics.quality['Log Diversity']?.toFixed(2) }}</el-col>
              </el-row>
              <el-row v-if="result.metrics.quality.BLEU !== undefined">
                <el-col :span="12">BLEU分数：</el-col>
                <el-col :span="12">{{ result.metrics.quality.BLEU?.toFixed(2) }}</el-col>
              </el-row>
            </template>

            <!-- 鲁棒性指标 -->
            <template v-if="result.metrics?.robustness">
              <el-row>
                <el-col :span="24">
                  <h4>鲁棒性指标</h4>
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">攻击前水印检测率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.robustness.watermark_detection_rate_before_attack * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">攻击后水印检测率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.robustness.watermark_detection_rate_after_attack * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">攻击成功率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.robustness.attack_success_rate * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
            </template>

            <!-- 可检测性指标 -->
            <template v-if="result.metrics?.detectability">
              <el-row>
                <el-col :span="24">
                  <h4>可检测性指标</h4>
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">准确率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.detectability.accuracy * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">精确率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.detectability.precision * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">召回率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.detectability.recall * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">F1分数：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.detectability.f1_score * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">误报率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.detectability.false_positive_rate * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="12">漏报率：</el-col>
                <el-col :span="12">
                  <el-progress
                    :percentage="result.metrics.detectability.false_negative_rate * 100"
                    :format="format"
                  />
                </el-col>
              </el-row>
            </template>

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
import { reactive, computed, onMounted, ref, watch } from 'vue'; // 引入Vue的相关函数
import { useWatermarkStore } from '@/stores'; // 引入水印存储
import { useDatasetStore } from '@/stores';
import { useTaskStore } from '@/stores/task';
import { ElMessage } from 'element-plus'; // 引入Element Plus的消息组件
import api from '@/api'; // 引入API模块

interface ResultState {
  metrics: {
    quality?: {
      PPL?: number;
      'Log Diversity'?: number;
      BLEU?: number;
    };
    robustness?: {
      watermark_detection_rate_before_attack: number;
      watermark_detection_rate_after_attack: number;
      attack_success_rate: number;
    };
    detectability?: {
      accuracy: number;
      precision: number;
      recall: number;
      f1_score: number;
      false_positive_rate: number;
      false_negative_rate: number;
    };
  } | null;
  details: Record<string, any> | null;
  attack: {
    success_rate: number;
    attacked_text: string;
    details: Record<string, any>;
  } | null;
}

interface Attacker {
  name: string;
  description: string;
  params: Record<string, any>;
}

const watermarkStore = useWatermarkStore(); // 获取水印存储实例
const datasetStore = useDatasetStore();
const taskStore = useTaskStore();

const currentTaskId = ref<string>('');
const taskStatus = ref<'pending' | 'processing' | 'completed' | 'failed'>('pending');
const taskError = ref<string>('');

const algorithms = computed(() => watermarkStore.algorithms); // 计算属性，获取水印算法列表
const datasets = computed(() => datasetStore.datasets);

const currentAlgorithmParams = computed(() => {
  const algo = algorithms.value.find(a => a.name === formData.algorithm);
  return algo?.params || {};
});

const currentAttackerParams = computed(() => {
  const attacker = attackers.find(a => a.name === attackData.type);
  return attacker?.params || {};
});

const getStepActive = computed(() => {
  switch (taskStatus.value) {
    case 'pending':
      return 0;
    case 'processing':
      return 1;
    case 'completed':
    case 'failed':
      return 2;
    default:
      return 0;
  }
});

const formData = reactive({
  dataset_id: '',
  algorithm: '',
  watermark_params: {} as Record<string, any>,
  metrics: [] as string[], // 评估指标
  quality_metrics: [] as string[], // 质量指标
});

const attackData = reactive({
  type: '',
  params: {} as Record<string, any>,
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

const attackers = reactive<Attacker[]>([]);

const format = (percentage: number) => percentage.toFixed(2) + '%'; // 格式化百分比

watch(() => formData.algorithm, () => {
  formData.watermark_params = { ...currentAlgorithmParams.value };
});

watch(() => attackData.type, () => {
  attackData.params = { ...currentAttackerParams.value };
});

const handleEvaluate = async () => {
  if (!formData.dataset_id || !formData.algorithm) {
    ElMessage.warning('请选择数据集和算法');
    return;
  }

  if (formData.metrics.length === 0) {
    ElMessage.warning('请选择至少一个评估指标');
    return;
  }

  if (formData.metrics.includes('quality') && formData.quality_metrics.length === 0) {
    ElMessage.warning('请选择至少一个质量指标');
    return;
  }

  try {
    loading.evaluate = true;
    const response = await api.evaluate.metrics({
      algorithm: formData.algorithm,
      metrics: formData.metrics,
      watermark_params: formData.watermark_params,
      dataset_id: formData.dataset_id,
      params: {
        ...(formData.metrics.includes('quality') ? {
          quality_metrics: formData.quality_metrics
        } : {}),
        ...(formData.metrics.includes('robustness') ? {
          attack_name: attackData.type
        } : {})
      },
      attack_params: formData.metrics.includes('robustness') ? attackData.params : undefined
    });

    currentTaskId.value = response.task_id;
    taskStatus.value = 'pending';
    taskError.value = '';
    
    taskStore.startPolling(
      response.task_id,
      (taskResponse) => {
        if (taskResponse.status === 'completed') {
          taskStatus.value = 'completed';
          result.metrics = taskResponse.result.metrics;
          result.details = taskResponse.result.details;
          currentTaskId.value = '';
          ElMessage.success('评估完成');
        } else if (taskResponse.status === 'failed') {
          taskStatus.value = 'failed';
          taskError.value = taskResponse.error || '任务执行失败';
          currentTaskId.value = '';
          ElMessage.error(taskResponse.error || '任务执行失败');
        } else {
          taskStatus.value = taskResponse.status;
        }
      },
      (error) => {
        taskStatus.value = 'failed';
        taskError.value = error;
        currentTaskId.value = '';
        ElMessage.error(error);
      }
    );
  } catch (error: any) {
    ElMessage.error(error.message || '评估失败');
    currentTaskId.value = '';
  } finally {
    loading.evaluate = false;
  }
};

const cancelTask = () => {
  if (currentTaskId.value) {
    taskStore.stopPolling(currentTaskId.value);
    taskStore.clearTask(currentTaskId.value);
    currentTaskId.value = '';
    taskStatus.value = 'pending';
    taskError.value = '';
    ElMessage.info('任务已取消');
  }
};

onMounted(async () => {
  try {
    await watermarkStore.fetchAlgorithms();
    await datasetStore.fetchDatasets();
    const response = await api.evaluate.getAttackers();
    attackers.splice(0, attackers.length, ...response);
  } catch (error: any) {
    ElMessage.error('获取算法列表失败');
  }
});
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

.task-status {
  padding: 20px;
}

.task-error {
  margin-top: 20px;
}
</style>