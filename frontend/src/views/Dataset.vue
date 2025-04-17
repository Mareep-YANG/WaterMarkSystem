<template>
  <div class="dataset-management">
    <div class="page-header">
      <h1>数据集管理</h1>
      <div class="action-buttons">
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon> 上传数据集
        </el-button>
        <el-button type="success" @click="showImportDialog = true">
          <el-icon><Download /></el-icon> 从HuggingFace导入
        </el-button>
      </div>
    </div>

    <!-- 数据集列表 -->
    <el-card class="dataset-list-card">
      <template #header>
        <div class="card-header">
          <span>我的数据集</span>
          <el-button type="primary" link @click="fetchDatasets">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="datasets" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="180" show-overflow-tooltip />
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="source" label="来源" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.source === 'uploaded' ? 'primary' : 'success'">
              {{ scope.row.source === 'uploaded' ? '上传' : 'HuggingFace' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" show-overflow-tooltip>
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="showDatasetDetail(scope.row)"
            >
              详情
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDeleteDataset(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传数据集对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传数据集"
      width="500px"
    >
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="uploadForm.name" placeholder="请输入数据集名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="uploadForm.description" 
            placeholder="请输入数据集描述" 
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="文件" prop="file">
          <el-upload
            class="dataset-upload"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 CSV、JSON、TXT 等格式
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpload" :loading="uploading">
            上传
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 从HuggingFace导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="从HuggingFace导入"
      width="500px"
    >
      <el-form :model="importForm" :rules="importRules" ref="importFormRef" label-width="120px">
        <el-form-item label="数据集名称" prop="datasetname">
          <el-input v-model="importForm.datasetname" placeholder="例如: squad" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="importForm.description" 
            placeholder="请输入数据集描述" 
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button type="primary" @click="handleImport" :loading="importing">
            导入
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 数据集详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="数据集详情"
      width="700px"
    >
      <div v-if="currentDataset" class="dataset-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentDataset.id }}</el-descriptions-item>
          <el-descriptions-item label="名称">{{ currentDataset.name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ currentDataset.description }}</el-descriptions-item>
          <el-descriptions-item label="来源">
            <el-tag :type="currentDataset.source === 'uploaded' ? 'primary' : 'success'">
              {{ currentDataset.source === 'uploaded' ? '上传' : 'HuggingFace' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDataset.status)">
              {{ getStatusText(currentDataset.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentDataset.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentDataset.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="行数">{{ currentDataset.num_rows }}</el-descriptions-item>
          <el-descriptions-item label="存储路径">{{ currentDataset.storage_path }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 显示任务状态 -->
    <TaskStatus v-if="currentTaskId" :task-id="currentTaskId" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { Upload, Download, Refresh } from '@element-plus/icons-vue';
import { useDatasetStore } from '@/stores';
import TaskStatus from '@/components/TaskStatus.vue';
import { Dataset } from '@/api';

// 数据和状态
const loading = ref(false);
const uploading = ref(false);
const importing = ref(false);
const datasets = ref<Dataset[]>([]);
const currentDataset = ref<Dataset | null>(null);
const currentTaskId = ref<string | null>(null);

// 对话框控制
const showUploadDialog = ref(false);
const showImportDialog = ref(false);
const showDetailDialog = ref(false);

// 表单引用
const uploadFormRef = ref<FormInstance>();
const importFormRef = ref<FormInstance>();

// 上传表单
const uploadForm = reactive({
  name: '',
  description: '',
  file: null as File | null
});

// 导入表单
const importForm = reactive({
  datasetname: '',
  description: ''
});

// 表单验证规则
const uploadRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入数据集描述', trigger: 'blur' },
    { min: 1, message: '描述不能为空', trigger: 'blur' }
  ]
});

const importRules = reactive<FormRules>({
  datasetname: [
    { required: true, message: '请输入数据集名称', trigger: 'blur' }
  ]
});

// 获取数据集列表
const fetchDatasets = async () => {
  loading.value = true;
  try {
    const datasetStore = useDatasetStore();
    await datasetStore.fetchDatasets();
    datasets.value = datasetStore.datasets;
  } catch (error) {
    ElMessage.error('加载数据集列表失败');
    console.error('Error loading datasets:', error);
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

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'processing':
      return 'warning';
    case 'failed':
      return 'danger';
    default:
      return 'info';
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return '已完成';
    case 'processing':
      return '处理中';
    case 'failed':
      return '失败';
    default:
      return '等待中';
  }
};

// 显示数据集详情
const showDatasetDetail = (dataset: Dataset) => {
  currentDataset.value = dataset;
  showDetailDialog.value = true;
};

// 处理文件选择
const handleFileChange = (file: any) => {
  if (file) {
    uploadForm.file = file.raw;
  }
};

// 上传数据集
const handleUpload = async () => {
  if (!uploadFormRef.value) return;
  
  try {
    // 验证表单
    await uploadFormRef.value.validate();
    
    // 检查文件
    if (!uploadForm.file) {
      ElMessage.warning('请选择文件');
      return;
    }

    // 检查描述是否为空
    if (!uploadForm.description?.trim()) {
      ElMessage.warning('请输入数据集描述');
      return;
    }

    uploading.value = true;
    
    // 创建 FormData
    const formData = new FormData();
    formData.append('file', uploadForm.file);
    formData.append('dataset_name', uploadForm.name.trim());
    formData.append('description', uploadForm.description.trim());
    formData.append('format_type', 'auto');

    // 上传文件
    const datasetStore = useDatasetStore();
    const taskId = await datasetStore.uploadDataset(formData);
    
    if (taskId) {
      currentTaskId.value = taskId;
      ElMessage.success('数据集上传任务已开始');
      showUploadDialog.value = false;
      
      // 重置表单
      uploadForm.name = '';
      uploadForm.description = '';
      uploadForm.file = null;
      if (uploadFormRef.value) {
        uploadFormRef.value.resetFields();
      }
    }
  } catch (error: any) {
    console.error('Upload error:', error);
    if (error.response?.status === 422) {
      const errorDetail = error.response.data.detail;
      if (Array.isArray(errorDetail)) {
        ElMessage.error(errorDetail[0].message || '上传失败：数据验证错误');
      } else {
        ElMessage.error(errorDetail || '上传失败：数据验证错误');
      }
    } else {
      ElMessage.error(error.message || '数据集上传失败');
    }
  } finally {
    uploading.value = false;
  }
};

// 从HuggingFace导入
const handleImport = async () => {
  if (!importFormRef.value) return;
  
  await importFormRef.value.validate(async (valid) => {
    if (valid) {
      importing.value = true;
      try {
        const datasetStore = useDatasetStore();
        const taskId = await datasetStore.importFromHuggingFace({
          dataset_name: importForm.datasetname,
          description: importForm.description
        });
        currentTaskId.value = taskId;
        
        ElMessage.success('数据集导入任务已开始');
        showImportDialog.value = false;
        
        // 重置表单
        importForm.datasetname = '';
        importForm.description = '';
        if (importFormRef.value) {
          importFormRef.value.resetFields();
        }
      } catch (error) {
        ElMessage.error('数据集导入失败');
        console.error('Error importing dataset:', error);
      } finally {
        importing.value = false;
      }
    }
  });
};

// 处理数据集删除
const handleDeleteDataset = async (datasetId: string) => {
  try {
    await ElMessageBox.confirm('确定要删除该数据集吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    const datasetStore = useDatasetStore();
    await datasetStore.deleteDataset(datasetId);
    ElMessage.success('删除成功');
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

// 监听任务状态变化
watch(() => useDatasetStore().currentTask, (task) => {
  if (task && task.status === 'completed') {
    currentTaskId.value = null;
    fetchDatasets();
  }
});

// 初始化加载数据集列表
onMounted(() => {
  fetchDatasets();
});
</script>

<style scoped>
.dataset-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.dataset-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dataset-upload {
  width: 100%;
}

.no-data {
  padding: 40px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.detail-loading {
  padding: 20px 0;
}
</style>
