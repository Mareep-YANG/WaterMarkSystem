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
      
      <el-table v-loading="loading" :data="datasetList" style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="scope">
            {{ scope.row.description || '无描述' }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.source === 'uploaded'" type="primary">上传</el-tag>
            <el-tag v-else-if="scope.row.source === 'huggingfacehub'" type="success">HuggingFace</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="numRows" label="行数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              link 
              @click="viewDataset(scope.row.id)"
            >查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && datasetList.length === 0" class="no-data">
        <el-empty description="暂无数据集" />
      </div>
    </el-card>

    <!-- 上传数据集对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传数据集"
      width="500px"
    >
      <el-form 
        :model="uploadForm" 
        label-position="top"
        :rules="uploadRules"
        ref="uploadFormRef"
      >
        <el-form-item label="数据集名称" prop="datasetname">
          <el-input v-model="uploadForm.datasetname" placeholder="请输入数据集名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="uploadForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入数据集描述（可选）" 
          />
        </el-form-item>
        
        <el-form-item label="文件格式" prop="formattype">
          <el-select v-model="uploadForm.formattype" placeholder="请选择文件格式" style="width: 100%">
            <el-option label="CSV" value="csv" />
            <el-option label="JSON" value="json" />
            <el-option label="Excel" value="excel" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="数据集文件" prop="file">
          <el-upload
            class="dataset-upload"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".csv,.json,.xlsx,.xls"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                请上传CSV、JSON或Excel文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitUpload" 
            :loading="uploading"
            :disabled="!uploadForm.file || !uploadForm.datasetname"
          >
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 从HuggingFace导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="从HuggingFace导入数据集"
      width="500px"
    >
      <el-form 
        :model="importForm" 
        label-position="top"
        :rules="importRules"
        ref="importFormRef"
      >
        <el-form-item label="HuggingFace数据集名称" prop="datasetname">
          <el-input 
            v-model="importForm.datasetname" 
            placeholder="请输入HuggingFace数据集名称"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="importForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入数据集描述（可选）" 
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitImport" 
            :loading="importing"
          >
            导入
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 数据集详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="数据集详情"
      width="600px"
    >
      <el-descriptions 
        v-if="currentDataset" 
        :column="1" 
        border
        :label-width="120"
      >
        <el-descriptions-item label="ID">{{ currentDataset.id }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ currentDataset.name }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentDataset.description || '无描述' }}</el-descriptions-item>
        <el-descriptions-item label="来源">
          <el-tag v-if="currentDataset.source === 'uploaded'" type="primary">用户上传</el-tag>
          <el-tag v-else-if="currentDataset.source === 'huggingfacehub'" type="success">HuggingFace Hub</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="行数">{{ currentDataset.numRows }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDataset.status)">
            {{ getStatusText(currentDataset.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="存储路径">{{ currentDataset.storagePath }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentDataset.createdAt) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(currentDataset.updatedAt) }}</el-descriptions-item>
      </el-descriptions>
      
      <div v-if="detailLoading" class="detail-loading">
        <el-skeleton :rows="6" animated />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { 
  Upload, 
  Download, 
  Refresh
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { datasets, createDatasetFormData } from '@/api'; // 直接从API导入

// 定义接口
interface Dataset {
  id: string;
  name: string;
  description: string | null;
  createdAt: string;
  updatedAt: string;
  source: 'uploaded' | 'huggingfacehub';
  numRows: number;
  storagePath: string;
  status: 'processing' | 'completed' | 'failed' | 'pending';
}

// 数据集列表
const datasetList = ref<Dataset[]>([]);
const loading = ref(false);

// 当前查看的数据集
const currentDataset = ref<Dataset | null>(null);
const detailLoading = ref(false);

// 对话框控制
const showUploadDialog = ref(false);
const showImportDialog = ref(false);
const showDetailDialog = ref(false);

// 上传表单
const uploadForm = ref({
  datasetname: '',
  description: '',
  formattype: 'csv',
  file: null as File | null
});

// 导入表单
const importForm = ref({
  datasetname: '',
  description: ''
});

// 状态标志
const uploading = ref(false);
const importing = ref(false);

// 表单校验规则
const uploadRules = {
  datasetname: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
  file: [{ required: true, message: '请上传数据集文件', trigger: 'change' }]
};

const importRules = {
  datasetname: [{ required: true, message: '请输入HuggingFace数据集名称', trigger: 'blur' }]
};

// 获取所有数据集
const fetchDatasets = async () => {
  loading.value = true;
  try {
    const response = await datasets.getDatasets();
    if (response.datasets && Array.isArray(response.datasets)) {
      // 如果响应是 {[]} 结构
      datasetList.value= response.datasets;
    } else if (Array.isArray(response)) {
      // 如果响应直接是数组
      datasetList.value = response;
    } 
  } catch (error) {
    console.error('获取数据集失败:', error);
    ElMessage.error('获取数据集列表失败');
  } finally {
    loading.value = false;
  }
};

// 查看数据集详情
const viewDataset = async (id: string) => {
  detailLoading.value = true;
  showDetailDialog.value = true;
  
  try {
    currentDataset.value = await datasets.getDatasetById(id);
  } catch (error) {
    console.error('获取数据集详情失败:', error);
    ElMessage.error('获取数据集详情失败');
  } finally {
    detailLoading.value = false;
  }
};

// 处理文件变更
const handleFileChange = (file: any) => {
  uploadForm.value.file = file.raw;
};

// 处理文件移除
const handleFileRemove = () => {
  uploadForm.value.file = null;
};

// 提交上传数据集
const submitUpload = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请上传数据集文件');
    return;
  }
  
  if (!uploadForm.value.datasetname) {
    ElMessage.warning('请输入数据集名称');
    return;
  }
  
  uploading.value = true;
  try {
    const formData = createDatasetFormData(
      uploadForm.value.file,
      uploadForm.value.datasetname,
      uploadForm.value.description,
      uploadForm.value.formattype
    );
    
    await datasets.uploadDataset(formData);
    ElMessage.success('数据集上传成功');
    
    // 重置表单并更新列表
    uploadForm.value = {
      datasetname: '',
      description: '',
      formattype: 'csv',
      file: null
    };
    showUploadDialog.value = false;
    fetchDatasets();
  } catch (error) {
    console.error('上传数据集失败:', error);
    ElMessage.error('数据集上传失败');
  } finally {
    uploading.value = false;
  }
};

// 提交导入数据集
const submitImport = async () => {
  if (!importForm.value.datasetname) {
    ElMessage.warning('请输入HuggingFace数据集名称');
    return;
  }
  
  importing.value = true;
  try {
    await datasets.importFromHuggingFace({
      datasetname: importForm.value.datasetname,
      description: importForm.value.description
    });
    
    ElMessage.success('已开始从HuggingFace导入数据集');
    
    // 重置表单并更新列表
    importForm.value = {
      datasetname: '',
      description: ''
    };
    showImportDialog.value = false;
    fetchDatasets();
  } catch (error) {
    console.error('导入数据集失败:', error);
    ElMessage.error('从HuggingFace导入数据集失败');
  } finally {
    importing.value = false;
  }
};

// 格式化时间显示
const formatTime = (time: string) => {
  return new Date(time).toLocaleString();
};

// 获取状态对应的标签类型
const getStatusType = (status: Dataset['status']) => {
  const typeMap: Record<Dataset['status'], string> = {
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info'
  };
  return typeMap[status];
};

// 获取状态文本
const getStatusText = (status: Dataset['status']) => {
  const textMap: Record<Dataset['status'], string> = {
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败',
    'pending': '等待中'
  };
  return textMap[status];
};

// 组件挂载时获取数据集列表
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
