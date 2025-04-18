import request from '@/utils/request';

// 模型接口定义
export interface Model {
  id: string;
  model_name: string;
  description?: string;
  is_loaded?: boolean;
  created_at?: string;
  updated_at?: string;
}
interface Dataset {
  id: string; // 数据集的唯一标识符
  name: string; // 数据集的名称
  description: string | null; // 数据集的描述
  created_at: string; // 数据集的创建时间
  updated_at: string; // 数据集的最后更新时间
  source: 'uploaded' | 'huggingface_hub'; // 数据集的来源
  num_rows: number; // 数据集中的行数
  storage_path: string; // 数据集的存储路径
  status: 'processing' | 'completed' | 'failed'| 'pending'; // 数据集的状态
}

// 任务相关接口定义
export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

// 认证相关接口
export const auth = {
  // 用户注册
  register: (data: { username: string; email: string; password: string }) =>
    request.post('/auth/register', data),

  // 用户登录
  login: (data: { username: string; password: string }) =>
    request.login(data.username, data.password).then((response) => {
      return {
        token: response.access_token,
        tokenType: response.token_type,
      };
    }),

  // 创建API密钥
  createApiKey: (description: string) =>
    request.post('/auth/api-keys', { description }),

  // 获取API密钥列表
  getApiKeys: () => request.get('/auth/api-keys'),

  // 撤销API密钥
  revokeApiKey: (id: string) => 
    request.delete(`/auth/api-keys/${id}`),

  // 获取用户信息
  getProfile: async () => {
    try {
      return await request.get('/auth/info');
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Token无效或已过期');
      }
      throw error;
    }
  },
};

// 水印相关接口
export const watermark = {
  // 获取支持的算法列表
  getAlgorithms: () => request.get('/watermark/algorithms'),

  // 嵌入水印
  embed: (data: {
    text: string;
    algorithm: string;
    key: string;
    params?: Record<string, any>;
  }) => request.post<TaskResponse>('/watermark/embed', data),

  // 检测水印
  detect: (data: {
    text: string;
    algorithm: string;
    key: string;
    params?: Record<string, any>;
  }) => request.post<TaskResponse>('/watermark/detect', data),

  // 可视化水印
  visualize: (data: {
    text: string;
    algorithm: string;
    key: string;
    params?: Record<string, any>;
  }) => request.post('/watermark/visualize', data),

  // 获取任务状态
  getTaskStatus: (taskId: string) => request.get<TaskResponse>(`/tasks/${taskId}`),
};

// 评估相关接口
export const evaluate = {
  // 评估指标
  metrics: (data: {
    algorithm: string;
    metrics: string[];
    watermark_params?: Record<string, any>;
    params?: Record<string, any>;
    attack_params?: Record<string, any>;
    dataset_id: string;
  }) => request.post<TaskResponse>('/evaluate/metrics', data),

  // 获取攻击算法列表
  getAttackers: () => request.post('/evaluate/attackers'),

  // 攻击测试
  attack: (data: {
    text: string;
    algorithm: string;
    key: string;
    attack_type: string;
    attack_params?: Record<string, any>;
  }) => request.post('/evaluate/attack', data),

  // 获取任务状态
  getTaskStatus: (taskId: string) => request.get<TaskResponse>(`/tasks/${taskId}`),
};

// 模型管理相关接口
export const models = {
  // 获取所有模型
  getModels: () => request.get<Model[]>('/model/models'),
  
  // 获取模型详情
  getModelById: (id: string) => request.get<Model>(`/model/${id}`),
  
  // 更新模型
  updateModel: (id: string, data: Model) => request.put(`/model/${id}`, data),
  
  // 添加新的 Huggingface 模型
  addModel: (data: { model_name: string; description: string }) => request.post('/model/add_model', data),

  // 从本地文件导入模型
  loadModel: (id: string) => request.post<TaskResponse>(`/model/${id}/load`),
  
  // 生成文本
  generateText: (id: string, data: { prompt: string; }) => request.post<TaskResponse>(`/model/${id}/generate`, data),
  
  // 删除模型
  deleteModel: (id: string) => request.delete(`/model/${id}`),
};

// 数据集管理相关接口
export const datasets = {
  // 获取所有数据集
  getDatasets: () => 
    request.get<Dataset[]>('/dataset/datasets'),
  
  // 获取数据集详情
  getDatasetById: (datasetId: string) => 
    request.get(`/dataset/datasets/${datasetId}`) as Promise<Dataset>,
  
  // 上传数据集
  uploadDataset: (formData: FormData) => 
    request.post<TaskResponse>('/dataset/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }),
  
  // 从HuggingFace导入数据集
  importFromHuggingFace: (params: {
    dataset_name: string;
    description?: string;
  }) => request.post<TaskResponse>(`/dataset/datasets/from_huggingface?dataset_name=${params.dataset_name}&description=${params.description || ''}`),

  // 删除数据集
  deleteDataset: (datasetId: string) => 
    request.delete(`/dataset/datasets/${datasetId}`),

  // 获取任务状态
  getTaskStatus: (taskId: string) => request.get<TaskResponse>(`/tasks/${taskId}`),
};
// 创建上传数据集的FormData助手函数
export const createDatasetFormData = (
  file: File,
  datasetname: string,
  description?: string,
  formattype?: string
): FormData => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('datasetname', datasetname);
  
  if (description) {
    formData.append('description', description);
  }
  
  if (formattype) {
    formData.append('formattype', formattype);
  }
  
  return formData;
};

export default {
  auth,
  watermark,
  evaluate,
  models,
  datasets,
};