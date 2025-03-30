import request from '@/utils/request';

// 模型接口定义
export interface Model {
  id: string;
  name: string;
  description?: string;
  size?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
}
export interface ModelImportParams {
  name: string;
  description?: string;
  file_path?: string;
  url?: string;
}

// 认证相关接口
export const auth = {
  // 用户注册
  register: (data: { username: string; email: string; password: string }) =>
    request.post('/auth/register', data),

  // 用户登录
  login: (data: { username: string; password: string }) =>
    request.post('/auth/login', data),

  // 创建API密钥
  createApiKey: (description: string) =>
    request.post('/auth/api-keys', { description }),

  // 获取API密钥列表
  getApiKeys: () => request.get('/auth/api-keys'),

  // 撤销API密钥
  revokeApiKey: (id: string) => 
    request.delete(`/auth/api-keys/${id}`),

  // 获取用户信息
  getProfile: () => request.get('/auth/me'),
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
  }) => request.post('/watermark/embed', data),

  // 检测水印
  detect: (data: {
    text: string;
    algorithm: string;
    key: string;
    params?: Record<string, any>;
  }) => request.post('/watermark/detect', data),

  // 可视化水印
  visualize: (data: {
    text: string;
    algorithm: string;
    key: string;
    params?: Record<string, any>;
  }) => request.post('/watermark/visualize', data),
};

// 评估相关接口
export const evaluate = {
  // 评估指标
  metrics: (data: {
    original_text: string;
    watermarked_text: string;
    algorithm: string;
    key: string;
    metrics: string[];
    params?: Record<string, any>;
  }) => request.post('/evaluate/metrics', data),

  // 攻击测试
  attack: (data: {
    text: string;
    algorithm: string;
    key: string;
    attack_type: string;
    attack_params?: Record<string, any>;
  }) => request.post('/evaluate/attack', data),
};

// 模型管理相关接口
export const models = {
  // 获取所有模型
  getModels: () => request.get<{models: Model[]}>('/models'),
  
  // 获取模型详情
  getModelById: (id: string) => request.get<Model>(`/models/${id}`),
  
  // 下载模型
  downloadModel: (id: string) => request.get<{download_url: string}>(`/models/${id}/download`),
  
  // 从本地文件导入模型
  importModelFromFile: (params: ModelImportParams) => 
    request.post<Model>('/models/import', params),
  
  // 从URL导入模型
  importModelFromUrl: (params: ModelImportParams) => 
    request.post<Model>('/models/import-from-url', params),
  
  // 删除模型
  deleteModel: (id: string) => request.delete<{success: boolean}>(`/models/${id}`),
};

export default {
  auth,
  watermark,
  evaluate,
  models,
};