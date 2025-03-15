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
                placeholder="请输入要处理的文本"
              />
            </el-form-item>

            <el-form-item label="密钥"><!-- 密钥输入区域 -->
              <el-input
                v-model="formData.key"
                placeholder="请输入水印密钥"
                show-password
              />
            </el-form-item>

            <el-form-item label="参数设置" v-if="currentAlgorithmParams"><!-- 参数设置区域 -->
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

            <div class="button-group"><!-- 按钮组 -->
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

      <el-col :span="12"><!-- 使用Element UI的el-col组件，设置列宽度为12 -->
        <el-card v-if="result.watermarked"><!-- 处理结果卡片 -->
          <template #header>
            <h3>处理结果</h3><!-- 处理结果标题 -->
          </template>
          
          <div class="result-content"><!-- 结果内容区域 -->
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
            
            <div v-if="result.visualization" class="visualization mt-20"><!-- 可视化结果区域 -->
              <h4>可视化结果</h4>
              <div ref="chartRef" class="chart-container"></div><!-- 图表容器 -->
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
import { ElMessage } from 'element-plus'; // 引入Element Plus的消息组件
import * as echarts from 'echarts'; // 引入ECharts库

const watermarkStore = useWatermarkStore(); // 获取水印存储实例
const chartRef = ref<HTMLElement>(); // 图表引用

const algorithms = computed(() => watermarkStore.algorithms); // 计算属性，获取算法列表
const currentAlgorithm = computed({
  get: () => watermarkStore.currentAlgorithm,
  set: (value) => watermarkStore.setCurrentAlgorithm(value || '')
}); // 计算属性，获取和设置当前算法

const currentAlgorithmParams = computed(() => {
  const algo = algorithms.value.find(a => a.name === currentAlgorithm.value);
  return algo?.params || {};
}); // 计算属性，获取当前算法的参数

const formData = reactive({
  text: '', // 输入文本
  key: '', // 密钥
  params: {} as Record<string, any> // 参数
});

const loading = reactive({
  embed: false, // 嵌入水印加载状态
  detect: false // 检测水印加载状态
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
  }
};

const handleEmbed = async () => {// 定义一个异步函数用于处理水印嵌入
  if (!formData.text || !formData.key) { // 检查文本和密钥是否输入
    ElMessage.warning('请输入文本和密钥');
    return;
  }

  try {
    loading.embed = true;// 开始嵌入水印，显示加载状态
    const response = await watermarkStore.embedWatermark(// 调用水印存储的方法嵌入水印
      formData.text,
      formData.key,
      formData.params
    );
    result.watermarked = response.watermarked_text;// 更新水印文本结果
    ElMessage.success('水印嵌入成功');// 显示成功消息
  } catch (error: any) {
    ElMessage.error(error.message || '水印嵌入失败');// 显示错误消息
  } finally {
    loading.embed = false;// 嵌入完成，隐藏加载状态
  }
};

const handleDetect = async () => {// 定义一个异步函数用于处理水印检测
  if (!result.watermarked || !formData.key) {// 检查是否已嵌入水印和密钥是否输入
    ElMessage.warning('请先嵌入水印');
    return;
  }

  try { 
    loading.detect = true;// 开始检测水印，显示加载状态
    const response = await watermarkStore.detectWatermark(// 调用水印存储的方法检测水印
      result.watermarked,
      formData.key,
      formData.params
    );
    result.detected = response.detected;
    result.confidence = response.confidence;
    result.visualization = response.details;// 更新检测结果
    
    if (result.visualization) {// 如果有可视化数据，更新图表
      nextTick(() => {
        updateVisualization(result.visualization);
      });
    }
  } catch (error: any) {
    ElMessage.error(error.message || '水印检测失败');// 显示错误消息
  } finally {
    loading.detect = false;// 检测完成，隐藏加载状态
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
</style>