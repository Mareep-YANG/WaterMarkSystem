import request from '@/utils/request';

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

export default {
  auth,
  watermark,
  evaluate,
};