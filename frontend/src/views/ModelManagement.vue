<template>
  <div class="model-management">
    <el-card class="model-header">
      <div class="header-content">
        <h1>大模型管理系统</h1>
        <el-button type="primary" @click="openAddModelDialog">添加模型</el-button>
      </div>
    </el-card>

    <!-- 模型列表 -->
    <el-card class="model-list">
      <el-table :data="modelsList" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="180" show-overflow-tooltip />
        <el-table-column prop="model_name" label="模型名称" width="180" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="is_loaded" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_loaded ? 'success' : 'warning'">
              {{ scope.row.is_loaded ? '已加载' : '未加载' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" show-overflow-tooltip>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              :disabled="scope.row.is_loaded" 
              @click="handleLoadModel(scope.row.id)"
            >
              加载
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              :disabled="!scope.row.is_loaded" 
              @click="openGenerateDialog(scope.row)"
            >
              文本生成
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDeleteModel(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加模型对话框 -->
    <el-dialog
      v-model="addModelDialogVisible"
      title="添加新模型"
      width="500px"
    >
      <el-form :model="modelForm" :rules="modelRules" ref="modelFormRef" label-width="100px">
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="modelForm.model_name" placeholder="输入Huggingface模型名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="modelForm.description" 
            placeholder="请输入模型描述" 
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span>
          <el-button @click="addModelDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddModel" :loading="submitting">
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 生成文本对话框 -->
    <el-dialog
      v-model="generateDialogVisible"
      title="生成文本" 
      width="650px"
    >
      <div v-if="currentModel">
        <h3>选中模型: {{ currentModel.model_name }}</h3>
        
        <el-form :model="generateForm" ref="generateFormRef" label-width="120px">
          <el-form-item label="输入文本" prop="text">
            <el-input 
              type="textarea" 
              v-model="generateForm.text" 
              placeholder="请输入提示文本"
              :rows="4"
            />
          </el-form-item>
          
          <el-form-item 
            label="攻击参数" 
            prop="attackparams" 
            v-if="generateForm.attacktype !== 'none'"
          >
            <el-input 
              type="textarea" 
              v-model="attackParamsJson" 
              placeholder="请以JSON格式输入攻击参数"
              :rows="3"
            />
            <div class="params-tip" v-if="paramsError">
              <el-alert
                :title="paramsError"
                type="error"
                :closable="false"
                show-icon
              />
            </div>
          </el-form-item>
        </el-form>
        
        <div v-if="generating" class="generating-indicator">
          <el-progress type="circle" :percentage="generatingProgress" />
          <p>正在生成文本...</p>
        </div>
        
        <div v-if="generatedText" class="generated-result">
          <h4>生成结果:</h4>
          <el-card shadow="never">
            <div class="text-content">{{ generatedText }}</div>
          </el-card>
        </div>
      </div>
      
      <template #footer>
        <span>
          <el-button @click="generateDialogVisible = false">关闭</el-button>
          <el-button 
            type="primary" 
            @click="handleGenerateText" 
            :loading="generating"
            :disabled="!isGenerateFormValid"
          >
            生成文本
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { models, Model } from '@/api/index';

// 数据和状态
const loading = ref(false);
const submitting = ref(false);
const generating = ref(false);
const generatingProgress = ref(0);
const modelsList = ref<Model[]>([]);
const currentModel = ref<Model | null>(null);
const generatedText = ref('');
const paramsError = ref('');

// 对话框控制
const addModelDialogVisible = ref(false);
const generateDialogVisible = ref(false);

// 表单引用
const modelFormRef = ref<FormInstance>();
const generateFormRef = ref<FormInstance>();

// 添加模型表单
const modelForm = reactive({
  model_name: '',
  description: ''
});

// 表单验证规则
const modelRules = reactive<FormRules>({
  model_name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 2, message: '模型名称长度至少2个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述不能超过500个字符', trigger: 'blur' }
  ]
});

// 生成文本表单
const generateForm = reactive({
  text: '',
  algorithm: 'greedy',
  key: '',
  attacktype: 'none',
  attackparams: {} as Record<string, any>
});

// 攻击参数JSON字符串
const attackParamsJson = ref('{}');

// 计算属性：验证JSON格式并转换为对象
watch(attackParamsJson, (newValue) => {
  try {
    generateForm.attackparams = JSON.parse(newValue);
    paramsError.value = '';
  } catch (e) {
    paramsError.value = '无效的JSON格式';
  }
});

// 计算属性：表单是否有效
const isGenerateFormValid = computed(() => {
  if (!generateForm.text) return false;
  if (generateForm.attacktype !== 'none' && paramsError.value) return false;
  return true;
});

// 加载模型列表
const loadModelsList = async () => {
  loading.value = true;
  try {
    const response = await models.getModels();
    // 处理不同可能的响应结构
    if (response.models && Array.isArray(response.models)) {
      // 如果响应是 {models: Model[]} 结构
      modelsList.value = response.models;
    } else if (Array.isArray(response)) {
      // 如果响应直接是数组
      modelsList.value = response;
    } 
  } catch (error) {
    ElMessage.error('加载模型列表失败');
    console.error('Error loading models:', error);
  } finally {
    loading.value = false;
  }
};

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString();
};

// 添加模型
const handleAddModel = async () => {
  if (!modelFormRef.value) return;
  
  await modelFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        await models.addModel({
          model_name: modelForm.model_name,
          description: modelForm.description
        });
        ElMessage.success('模型添加成功');
        addModelDialogVisible.value = false;
        loadModelsList();
      } catch (error) {
        ElMessage.error('添加模型失败');
        console.error('Error adding model:', error);
      } finally {
        submitting.value = false;
      }
    }
  });
};

// 打开添加模型对话框
const openAddModelDialog = () => {
  modelForm.model_name = '';
  modelForm.description = '';
  addModelDialogVisible.value = true;
};

// 加载模型
const handleLoadModel = async (id: string) => {
  try {
    loading.value = true;
    await models.loadModel(id);
    ElMessage.success('模型加载成功');
    loadModelsList(); // 刷新列表
  } catch (error) {
    ElMessage.error('模型加载失败');
    console.error('Error loading model:', error);
  } finally {
    loading.value = false;
  }
};

// 删除模型
const handleDeleteModel = (id: string) => {
  ElMessageBox.confirm(
    '确定要删除该模型吗？此操作不可恢复。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  .then(async () => {
    try {
      loading.value = true;
      await models.deleteModel(id);
      ElMessage.success('模型删除成功');
      loadModelsList(); // 刷新列表
    } catch (error) {
      ElMessage.error('删除模型失败');
      console.error('Error deleting model:', error);
    } finally {
      loading.value = false;
    }
  })
  .catch(() => {
    // 用户取消删除操作
  });
};

// 打开文本生成对话框
const openGenerateDialog = (model: Model) => {
  currentModel.value = model;
  generateForm.text = '';
  generateForm.algorithm = 'greedy';
  generateForm.key = '';
  generateForm.attacktype = 'none';
  generateForm.attackparams = {};
  attackParamsJson.value = '{}';
  generatedText.value = '';
  generateDialogVisible.value = true;
};

// 模拟生成进度
const simulateProgress = () => {
  generatingProgress.value = 0;
  const interval = setInterval(() => {
    generatingProgress.value += 10;
    if (generatingProgress.value >= 100) {
      clearInterval(interval);
    }
  }, 300);
  return interval;
};

// 生成文本
const handleGenerateText = async () => {
  if (!currentModel.value || !isGenerateFormValid.value) return;
  
  generating.value = true;
  generatedText.value = '';
  
  // 模拟进度条
  const progressInterval = simulateProgress();
  
  try {
    const data = {
      prompt: generateForm.text,
    };
    
    // 只有当选择了攻击类型时才添加攻击参数
    if (generateForm.attacktype !== 'none') {
      Object.assign(data, { attackparams: generateForm.attackparams });
    }
    
    const response = await models.generateText(currentModel.value.id, data);
    generatedText.value = response.generated_text || JSON.stringify(response);
    ElMessage.success('文本生成成功');
  } catch (error) {
    ElMessage.error('文本生成失败');
    console.error('Error generating text:', error);
  } finally {
    clearInterval(progressInterval);
    generatingProgress.value = 100;
    generating.value = false;
  }
};

// 组件挂载时加载模型列表
onMounted(() => {
  loadModelsList();
});
</script>

<style scoped>
.model-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.model-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-list {
  margin-bottom: 20px;
}

.generating-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
}

.generated-result {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.text-content {
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.params-tip {
  margin-top: 8px;
}
</style>
