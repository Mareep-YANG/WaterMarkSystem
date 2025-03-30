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

// 认证相关接口
export const auth = {
  // 用户注册
  register: (data: { username: string; email: string; password: string }) =>
    request.post('/auth/register', data),

  // 用户登录
  login: (data: { username: string; password: string }) =>
    request.login(data.username, data.password),

  // 创建API密钥
  createApiKey: (description: string) =>
    request.post('/auth/api-keys', { description }),

  // 获取API密钥列表
  getApiKeys: () => request.get('/auth/api-keys'),

  // 撤销API密钥
  revokeApiKey: (id: string) => 
    request.delete(`/auth/api-keys/${id}`),

  // 获取用户信息
  getProfile: () => request.get('/auth/info'),
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
  getModels: () => request.get<{models: Model[]}>('/api/v1/model/models'),
  
  // 获取模型详情
  getModelById: (id: string) => request.get<Model>(`/model/${id}`),
  
  // 更新模型
  updateModel: (id: string, data: Model) => request.put(`/api/v1/model/${id}`, data),
  
  // 添加新的 Huggingface 模型
  addModel: (data: { model_name: string; description: string }) => request.post('/api/v1/model/addmodel', data),

  // 从本地文件导入模型
  loadModel: (id: string) => request.post(`/api/v1/model/${id}/load`),
  
  // 生成文本
  generateText: (id: string, data: { text: string; algorithm: string; key: string; attacktype: string; attackparams?: Record<string, any> }) => request.post(`/api/v1/model/${id}/generate`, data),
  
  // 删除模型
  deleteModel: (id: string) => request.delete(`/api/v1/model/${id}`),
};

export default {
  auth,
  watermark,
  evaluate,
  models,
};