<template>
  <div class="watermark-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>水印处理</h3>
              <el-select v-model="currentAlgorithm" placeholder="选择算法">
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
            </div>
          </template>

          <el-form :model="formData" label-position="top">
            <el-form-item label="输入文本">
              <el-input
                v-model="formData.text"
                type="textarea"
                :rows="6"
                placeholder="请输入要处理的文本"
              />
            </el-form-item>

            <el-form-item label="密钥">
              <el-input
                v-model="formData.key"
                placeholder="请输入水印密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="参数设置" v-if="currentAlgorithmParams">
              <el-collapse>
                <el-collapse-item title="高级参数">
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
                </el-collapse-item>
              </el-collapse>
            </el-form-item>

            <div class="button-group">
              <el-button
                type="primary"
                :loading="loading.embed"
                @click="handleEmbed"
              >
                嵌入水印
              </el-button>
              <el-button
                type="success"
                :loading="loading.detect"
                @click="handleDetect"
              >
                检测水印
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card v-if="result.watermarked">
          <template #header>
            <h3>处理结果</h3>
          </template>
          
          <div class="result-content">
            <el-alert
              v-if="result.detected"
              :title="'检测到水印，置信度: ' + (result.confidence * 100).toFixed(2) + '%'"
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
            
            <div v-if="result.visualization" class="visualization mt-20">
              <h4>可视化结果</h4>
              <div ref="chartRef" class="chart-container"></div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue';
import { useWatermarkStore } from '@/stores';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';

const watermarkStore = useWatermarkStore();
const chartRef = ref<HTMLElement>();

const algorithms = computed(() => watermarkStore.algorithms);
const currentAlgorithm = computed({
  get: () => watermarkStore.currentAlgorithm,
  set: (value) => watermarkStore.setCurrentAlgorithm(value || '')
});

const currentAlgorithmParams = computed(() => {
  const algo = algorithms.value.find(a => a.name === currentAlgorithm.value);
  return algo?.params || {};
});

const formData = reactive({
  text: '',
  key: '',
  params: {} as Record<string, any>
});

const loading = reactive({
  embed: false,
  detect: false
});

const result = reactive({
  watermarked: '',
  detected: false,
  confidence: 0,
  visualization: null as any
});

watch(currentAlgorithm, () => {
  formData.params = { ...currentAlgorithmParams.value };
});

const updateVisualization = (data: any) => {
  if (!chartRef.value || !data) return;
  
  const chart = echarts.init(chartRef.value);
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
    });
  } else if (data.type === 'heatmap') {
    // 实现热力图可视化
  }
};

const handleEmbed = async () => {
  if (!formData.text || !formData.key) {
    ElMessage.warning('请输入文本和密钥');
    return;
  }

  try {
    loading.embed = true;
    const response = await watermarkStore.embedWatermark(
      formData.text,
      formData.key,
      formData.params
    );
    result.watermarked = response.watermarked_text;
    ElMessage.success('水印嵌入成功');
  } catch (error: any) {
    ElMessage.error(error.message || '水印嵌入失败');
  } finally {
    loading.embed = false;
  }
};

const handleDetect = async () => {
  if (!result.watermarked || !formData.key) {
    ElMessage.warning('请先嵌入水印');
    return;
  }

  try {
    loading.detect = true;
    const response = await watermarkStore.detectWatermark(
      result.watermarked,
      formData.key,
      formData.params
    );
    result.detected = response.detected;
    result.confidence = response.confidence;
    result.visualization = response.details;
    
    if (result.visualization) {
      nextTick(() => {
        updateVisualization(result.visualization);
      });
    }
  } catch (error: any) {
    ElMessage.error(error.message || '水印检测失败');
  } finally {
    loading.detect = false;
  }
};

onMounted(async () => {
  try {
    await watermarkStore.fetchAlgorithms();
    formData.params = { ...currentAlgorithmParams.value };
  } catch (error) {
    ElMessage.error('获取算法列表失败');
  }
});
</script>

<style scoped>
.watermark-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.visualization {
  border-top: 1px solid #dcdfe6;
  padding-top: 20px;
}

.chart-container {
  height: 300px;
  margin-top: 10px;
}
</style>