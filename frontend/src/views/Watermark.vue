<template>
  <div class="watermark-container"><!-- 水印处理页面的容器 -->
    <el-row :gutter="20"><!-- 使用Element UI的el-row组件，设置列间距为20 -->
      <el-col :span="12"><!-- 使用Element UI的el-col组件，设置列宽度为12 -->
        <el-card><!-- 水印处理卡片 -->
          <template #header><!-- 头部模板区域 -->
            <div class="card-header">
              <h3>水印处理</h3><!-- 水印处理标题 -->
              <el-select v-model="currentAlgorithm" placeholder="选择算法"><!-- 算法选择下拉框 -->
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
                    <span>{{ algo.name }}</span><!-- 算法名称 -->
                  </el-tooltip>
                </el-option>
              </el-select>
            </div>
          </template>

          <el-form :model="formData" label-position="top"><!-- 表单区域 -->
            <el-form-item label="输入文本"><!-- 输入文本区域 -->
              <el-input
                v-model="formData.text"
                type="textarea"
                :rows="6"
                placeholder="请输入Prompt"
              />
            </el-form-item>



            <el-form-item label="参数设置" v-if="currentAlgorithmParams">
              <template v-for="(value, key) in currentAlgorithmParams" :key="key">
                <el-form-item :label="key">
                  <el-input-number
                    v-if="typeof value === 'number'"
                    v-model="formData.params[key]"
                    :min="0"
                    :step="0.1"
                  />
                  <el-input
                    v-else
                    v-model="formData.params[key]"
                  />
                </el-form-item>
              </template>
            </el-form-item>

            <div class="button-group"><!-- 按钮组 -->
              <el-button
                type="primary"
                :loading="loading.embed"
                @click="handleEmbed"
                :disabled="!!currentTaskId"
              >
                嵌入水印
              </el-button>
              <el-button
                type="success"
                :loading="loading.detect"
                @click="handleDetect"
                :disabled="!!currentTaskId"
              >
                检测水印
              </el-button>
              <el-button
                type="info"
                :loading="loading.visualize"
                @click="handleVisualize"
                :disabled="!result.watermarked || !!currentTaskId"
              >
                可视化分析
              </el-button>
            </div>
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

        <el-card v-if="result.watermarked"><!-- 处理结果卡片 -->
          <template #header>
            <h3>处理结果</h3><!-- 处理结果标题 -->
          </template>
          
          <div class="result-content"><!-- 结果内容区域 -->
            <el-alert
              v-if="result.detected"
              :title="'检测到水印，置信度: ' + (result.confidence ).toFixed(2) "
              type="success"
              :closable="false"
            />
            <el-alert
              v-if="result.detected === false"
              title="未检测到水印"
              type="warning"
              :closable="false"
            />
            
            <el-input
              v-model="result.watermarked"
              type="textarea"
              :rows="6"
              readonly
              class="mt-20"
            />
            
            <div v-if="result.visualization" class="visualization mt-20"><!-- 可视化结果区域 -->
              <h4>可视化结果</h4>
              <div v-if="currentAlgorithm === 'dip'" class="highlighted-text">
                <template v-for="(token, index) in result.visualization.decoded_tokens" :key="index">
                  <span 
                    v-if="token !== '\n'"
                    :class="{
                      'highlight-positive': result.visualization.highlight_values[index] > 0,
                      'highlight-negative': result.visualization.highlight_values[index] < 0,
                      'highlight-neutral': result.visualization.highlight_values[index] === 0
                    }"
                    :title="'水印强度: ' + result.visualization.highlight_values[index]"
                  >
                    {{ token === ' ' ? '␣' : token }}
                  </span>
                  <br v-else />
                </template>
              </div>
              <div v-else ref="chartRef" class="chart-container"></div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'; // 引入Vue的相关函数
import { useWatermarkStore } from '@/stores'; // 引入水印存储
import { useTaskStore } from '@/stores/task';
import { ElMessage } from 'element-plus'; // 引入Element Plus的消息组件
import * as echarts from 'echarts'; // 引入ECharts库
import api from '@/api';

const watermarkStore = useWatermarkStore(); // 获取水印存储实例
const taskStore = useTaskStore();
const chartRef = ref<HTMLElement>(); // 图表引用

const currentTaskId = ref<string>('');
const taskStatus = ref<'pending' | 'processing' | 'completed' | 'failed'>('pending');
const taskError = ref<string>('');

const algorithms = computed(() => watermarkStore.algorithms); // 计算属性，获取算法列表
const currentAlgorithm = computed({
  get: () => watermarkStore.currentAlgorithm || '',
  set: (value: string) => watermarkStore.setCurrentAlgorithm(value)
}); // 计算属性，获取和设置当前算法

const currentAlgorithmParams = computed(() => {
  if (!currentAlgorithm.value) return {};
  const algo = algorithms.value.find((a: { name: string; params: Record<string, any> }) => a.name === currentAlgorithm.value);
  return algo?.params || {};
}); // 计算属性，获取当前算法的参数

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
  text: '', // 输入文本
  key: '', // 密钥
  params: {} as Record<string, any> // 参数
});

const loading = reactive({
  embed: false, // 嵌入水印加载状态
  detect: false, // 检测水印加载状态
  visualize: false // 可视化分析加载状态
});

const result = reactive({
  watermarked: '', // 水印后的文本
  detected: false, // 是否检测到水印
  confidence: 0, // 检测置信度
  visualization: null as any // 可视化结果
});

watch(currentAlgorithm, () => {
  formData.params = { ...currentAlgorithmParams.value };
}); // 监听当前算法变化，更新参数

const updateVisualization = (data: any) => {// 定义一个函数用于更新图表可视化
  if (!chartRef.value || !data) return;// 检查图表引用和数据是否存在
  
  const chart = echarts.init(chartRef.value); // 初始化图表，根据数据类型设置图表选项
  if (data.type === 'line_chart') {
    chart.setOption({
      xAxis: { type: 'category', data: data.data.labels },
      yAxis: { type: 'value' },
      series: data.data.datasets.map((dataset: any) => ({
        name: dataset.label,
        type: 'line',
        data: dataset.data,
        smooth: true
      }))
    }); // 设置折线图选项
  } else if (data.type === 'heatmap') {
    // 实现热力图可视化
  } else if (data.decoded_tokens && data.highlight_values) {
    // 实现token级别的可视化
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: function(params: any) {
          const token = data.decoded_tokens[params[0].dataIndex];
          const value = params[0].value;
          return `Token: ${token}<br/>水印强度: ${value}`;
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.decoded_tokens,
        axisLabel: {
          interval: 0,
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: '水印强度',
        min: -1,
        max: 1
      },
      series: [{
        name: '水印强度',
        type: 'bar',
        data: data.highlight_values.map((value: number) => ({
          value: value,
          itemStyle: {
            color: value > 0 ? '#91cc75' : value < 0 ? '#ee6666' : '#5470c6'
          }
        })),
        barWidth: '60%'
      }]
    };
    chart.setOption(option);
  }
};

const handleEmbed = async () => {
  if (!formData.text) {
    ElMessage.warning('请输入文本');
    return;
  }

  try {
    loading.embed = true;
    const taskId = await watermarkStore.embedWatermark(
      formData.text,
      formData.params
    );
    
    currentTaskId.value = taskId;
    taskStatus.value = 'pending';
    taskError.value = '';
    
    taskStore.startPolling(
      taskId,
      (taskResponse) => {
        if (taskResponse.status === 'completed') {
          taskStatus.value = 'completed';
          result.watermarked = taskResponse.result.watermarked_text;
          currentTaskId.value = '';
          ElMessage.success('水印嵌入成功');
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
    ElMessage.error(error.message || '水印嵌入失败');
    currentTaskId.value = '';
  } finally {
    loading.embed = false;
  }
};

const handleDetect = async () => {
  if (!result.watermarked) {
    ElMessage.warning('请先嵌入水印');
    return;
  }

  try { 
    loading.detect = true;
    const taskId = await watermarkStore.detectWatermark(
      result.watermarked,
      formData.params
    );
    
    currentTaskId.value = taskId;
    taskStatus.value = 'pending';
    taskError.value = '';
    
    taskStore.startPolling(
      taskId,
      async (taskResponse) => {
        if (taskResponse.status === 'completed') {
          taskStatus.value = 'completed';
          result.detected = taskResponse.result.detected;
          result.confidence = taskResponse.result.confidence;
          currentTaskId.value = '';
          ElMessage.success('水印检测完成');
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
    ElMessage.error(error.message || '水印检测失败');
    currentTaskId.value = '';
  } finally {
    loading.detect = false;
  }
};

const handleVisualize = async () => {
  if (!result.watermarked) {
    ElMessage.warning('请先嵌入水印');
    return;
  }

  try {
    loading.visualize = true;
    const visualizationData = await api.watermark.visualize({
      text: result.watermarked,
      algorithm: currentAlgorithm.value,
      params: formData.params
    });
    result.visualization = visualizationData;
    if (result.visualization) {
      nextTick(() => {
        updateVisualization(result.visualization);
      });
    }
    ElMessage.success('可视化分析完成');
  } catch (error: any) {
    console.error('获取可视化数据失败:', error);
    ElMessage.error('可视化分析失败');
  } finally {
    loading.visualize = false;
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

onMounted(async () => {// 组件挂载时执行的函数
  try {
    await watermarkStore.fetchAlgorithms();// 获取水印算法列表
    formData.params = { ...currentAlgorithmParams.value };// 设置当前算法参数
  } catch (error) {
    ElMessage.error('获取算法列表失败');// 显示错误消息
  }
});
</script>

<style scoped>
.watermark-container {
  padding: 20px; /* 设置容器内边距 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* 设置头部内容的对齐方式 */
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px; /* 设置按钮组的上边距 */
}

.mt-20 {
  margin-top: 20px; /* 设置上边距 */
}

.visualization {
  border-top: 1px solid #dcdfe6; /* 设置可视化区域的上边框 */
  padding-top: 20px; /* 设置可视化区域的上内边距 */
}

.chart-container {
  height: 300px; /* 设置图表容器高度 */
  margin-top: 10px; /* 设置图表容器的上边距 */
}

.task-status {
  padding: 20px;
}

.task-error {
  margin-top: 20px;
}

.highlighted-text {
  font-size: 16px;
  line-height: 1.8;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;
  word-break: break-word;
}

.highlight-positive {
  background-color: rgba(145, 204, 117, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: inline-block;
}

.highlight-negative {
  background-color: rgba(238, 102, 102, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: inline-block;
}

.highlight-neutral {
  background-color: rgba(84, 112, 198, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.3s ease;
  display: inline-block;
}

.highlighted-text span {
  margin: 0 1px;
}
</style>