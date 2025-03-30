<template>
  <div class="model-management">
    <!-- 模型管理页面的主要卡片 -->
    <el-card class="model-section">
      <template #header>
        <div class="card-header">
          <span>Available Models</span>
          <!-- 打开导入模型对话框的按钮 -->
          <el-button type="primary" @click="openImportDialog">Import Model</el-button>
        </div>
      </template>

      <!-- 模型列表表格 -->
      <el-table v-loading="loading" :data="models" style="width: 100%">
        <!-- 模型名称列 -->
        <el-table-column prop="name" label="Name" />
        <!-- 模型描述列 -->
        <el-table-column prop="description" label="Description" />
        <!-- 模型大小列 -->
        <el-table-column prop="size" label="Size" width="120" />
        <!-- 模型状态列 -->
        <el-table-column prop="status" label="Status" width="120">
          <template #default="scope">
            <!-- 根据状态动态显示标签 -->
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <!-- 操作列 -->
        <el-table-column label="Actions" width="250">
          <template #default="scope">
            <!-- 下载按钮 -->
            <el-button type="primary" size="small" @click="handleDownload(scope.row)">
              Download
            </el-button>
            <!-- 查看详情按钮 -->
            <el-button type="info" size="small" @click="handleViewDetails(scope.row)">
              Details
            </el-button>
            <!-- 删除按钮 -->
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 导入模型对话框 -->
    <el-dialog v-model="importDialogVisible" title="Import Model" width="500px">
      <!-- 导入方式选项卡 -->
      <el-tabs v-model="importType">
        <!-- 从 URL 导入 -->
        <el-tab-pane label="From URL" name="url">
          <el-form :model="importForm" label-width="120px">
            <!-- 模型名称输入框 -->
            <el-form-item label="Model Name" required>
              <el-input v-model="importForm.name" placeholder="Enter model name" />
            </el-form-item>
            <!-- 模型描述输入框 -->
            <el-form-item label="Description">
              <el-input 
                v-model="importForm.description" 
                type="textarea" 
                placeholder="Enter model description"
              />
            </el-form-item>
            <!-- 模型 URL 输入框 -->
            <el-form-item label="URL" required>
              <el-input v-model="importForm.url" placeholder="https://example.com/model.bin" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 从本地文件导入 -->
        <el-tab-pane label="From Local File" name="file">
          <el-form :model="importForm" label-width="120px">
            <!-- 模型名称输入框 -->
            <el-form-item label="Model Name" required>
              <el-input v-model="importForm.name" placeholder="Enter model name" />
            </el-form-item>
            <!-- 模型描述输入框 -->
            <el-form-item label="Description">
              <el-input 
                v-model="importForm.description" 
                type="textarea" 
                placeholder="Enter model description"
              />
            </el-form-item>
            <!-- 文件路径输入框 -->
            <el-form-item label="File Path" required>
              <el-input v-model="importForm.file_path" placeholder="/path/to/model.bin" />
              <!-- 浏览文件路径按钮 -->
              <el-button style="margin-top: 8px" @click="selectFilePath">
                Browse File Path
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- 对话框底部按钮 -->
      <template #footer>
        <span class="dialog-footer">
          <!-- 取消按钮 -->
          <el-button @click="importDialogVisible = false">Cancel</el-button>
          <!-- 导入按钮 -->
          <el-button type="primary" @click="handleImport" :loading="importing">
            Import
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 模型详情对话框 -->
    <el-dialog v-model="detailsDialogVisible" title="Model Details" width="600px">
      <div v-if="selectedModel">
        <!-- 模型详情描述 -->
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ID">{{ selectedModel.id }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ selectedModel.name }}</el-descriptions-item>
          <el-descriptions-item label="Description">{{ selectedModel.description }}</el-descriptions-item>
          <el-descriptions-item label="Size">{{ selectedModel.size }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedModel.status)">{{ selectedModel.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Created At">{{ formatDate(selectedModel.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="Updated At">{{ formatDate(selectedModel.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
// 引入 Vue 的 ref 和生命周期钩子
import { ref, onMounted } from 'vue';
// 引入 Element Plus 的消息提示和消息框组件
import { ElMessage, ElMessageBox } from 'element-plus';
// 引入 API 模块和类型定义
import api, { Model, ModelImportParams } from '@/api';

// 定义响应式变量
const models = ref<Model[]>([]); // 模型列表
const loading = ref(false); // 加载状态
const importing = ref(false); // 导入状态
const importDialogVisible = ref(false); // 导入对话框可见性
const detailsDialogVisible = ref(false); // 详情对话框可见性
const selectedModel = ref<Model | null>(null); // 当前选中的模型
const importType = ref('url'); // 导入类型（URL 或文件）
const importForm = ref<ModelImportParams>({
  name: '',
  description: '',
  url: '',
  file_path: ''
});

// 页面加载时获取模型列表
onMounted(() => {
  fetchModels();
});

// 获取模型列表的函数
const fetchModels = async () => {
  loading.value = true;
  try {
    const response = await api.models.getModels();
    models.value = response.models;
  } catch (error) {
    ElMessage.error('获取模型列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 打开导入对话框
const openImportDialog = () => {
  importForm.value = {
    name: '',
    description: '',
    url: '',
    file_path: ''
  };
  importDialogVisible.value = true;
};

// 处理模型导入
const handleImport = async () => {
  if (!importForm.value.name) {
    return ElMessage.warning('Model name is required');
  }

  importing.value = true;

  try {
    if (importType.value === 'url') {
      if (!importForm.value.url) {
        return ElMessage.warning('URL is required');
      }
      await api.models.importModelFromUrl(importForm.value);
      ElMessage.success('Model import from URL initiated successfully');
    } else {
      if (!importForm.value.file_path) {
        return ElMessage.warning('File path is required');
      }
      await api.models.importModelFromFile(importForm.value);
      ElMessage.success('Model import from file initiated successfully');
    }

    importDialogVisible.value = false;
    fetchModels(); 
  } catch (error) {
    ElMessage.error('Failed to import model');
    console.error(error);
  } finally {
    importing.value = false;
  }
};

// 处理模型下载
const handleDownload = async (model: Model) => {
  try {
    const response = await api.models.downloadModel(model.id);
    const link = document.createElement('a');
    link.href = response.download_url;
    link.download = model.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    ElMessage.success('Download started');
  } catch (error) {
    ElMessage.error('Failed to download model');
    console.error(error);
  }
};

// 处理模型删除
const handleDelete = (model: Model) => {
  ElMessageBox.confirm(
    `Are you sure you want to delete model "${model.name}"?`,
    'Warning',
    {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await api.models.deleteModel(model.id);
        ElMessage.success('Model deleted successfully');
        fetchModels(); 
      } catch (error) {
        ElMessage.error('Failed to delete model');
        console.error(error);
      }
    })
    .catch(() => {
    });
};

// 查看模型详情
const handleViewDetails = async (model: Model) => {
  try {
    const detailedModel = await api.models.getModelById(model.id);
    selectedModel.value = detailedModel;
    detailsDialogVisible.value = true;
  } catch (error) {
    ElMessage.error('Failed to fetch model details');
    console.error(error);
  }
};

// 模拟选择文件路径
const selectFilePath = () => {
  ElMessage.info('In a production environment, this would open a file browser');
  importForm.value.file_path = '/models/custom_model.bin';
};

// 根据状态返回标签类型
const getStatusType = (status?: string) => {
  if (!status) return '';

  switch (status.toLowerCase()) {
    case 'available':
      return 'success';
    case 'downloading':
    case 'importing':
      return 'warning';
    case 'error':
      return 'danger';
    default:
      return 'info';
  }
};

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString();
};
</script>

<style scoped>
/* 页面样式 */
.model-management {
  padding: 20px;
}

.model-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
