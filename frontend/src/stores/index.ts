import { defineStore } from 'pinia';
import api from '@/api';
import router from '@/router';
import { ElMessage } from 'element-plus';
import { useTaskStore } from '@/stores/task';
import { Model } from '@/api';

// 重新导出useTaskStore
export { useTaskStore };

interface Dataset {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  source: 'uploaded' | 'huggingface_hub';
  num_rows: number;
  storage_path: string;
  status: 'processing' | 'completed' | 'failed' | 'pending';
}

interface UserState {
  token: string | null;
  tokenType: string | null; // 添加 tokenType 属性
  profile: {
    username: string;
    email: string;
    is_active: boolean;
  } | null;
}

interface WatermarkState {
  algorithms: {
    name: string;
    description: string;
    type: string;
    params: Record<string, any>;
  }[];
  currentAlgorithm: string | null;
}

// 用户状态管理
export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('token') || null,
    tokenType: localStorage.getItem('tokenType') || null,
    profile: null,
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  
  actions: {
    setToken(token: string,  tokenType: string) {
      this.token = token;
      this.tokenType = tokenType; // 确保 tokenType 被正确设置

      localStorage.setItem('token', token);
      localStorage.setItem('tokenType', tokenType); // 保存 tokenType
    },
    
    async fetchProfile() {
      try {
        const profile = await api.auth.getProfile();
        this.profile = profile;
      } catch (error) {
        this.profile = null;
        throw error;
      }
    },
    
    async login(username: string, password: string) {
      try {
        const response = await api.auth.login({ username, password });
        
        this.setToken(response.token, response.tokenType); // 添加 tokenType 参数
        
        await this.fetchProfile();
        return true;
      } catch (error) {
        throw error;
      }
    },
    
    checkTokenExpiry() {
      ElMessage.warning('您的会话已过期，请重新登录');
      this.logout();
      return false;
    },

    logout() {
      this.token = null;
      this.tokenType = null; // 清除 tokenType
      this.profile = null;
      localStorage.removeItem('token');
      localStorage.removeItem('tokenType'); // 移除 tokenType      
      // 还需要重定向到登录页
      router.push('/login');
    },
  },
});

// 水印功能状态管理
export const useWatermarkStore = defineStore('watermark', {
  state: (): WatermarkState => ({
    algorithms: [],
    currentAlgorithm: null,
  }),
  
  actions: {
    async fetchAlgorithms() {
      try {
        const algorithms = await api.watermark.getAlgorithms();
        this.algorithms = algorithms;
        if (algorithms.length > 0) {
          this.currentAlgorithm = algorithms[0].name;
        }
      } catch (error) {
        console.error('Failed to fetch algorithms:', error);
        throw error;
      }
    },
    
    setCurrentAlgorithm(algorithm: string) {
      this.currentAlgorithm = algorithm;
    },
    
    async embedWatermark(text: string, key: string, params?: Record<string, any>) {
      if (!this.currentAlgorithm) {
        throw new Error('No algorithm selected');
      }
      const response = await api.watermark.embed({
        text,
        algorithm: this.currentAlgorithm,
        key,
        params,
      });

      if (!response || !response.task_id) {
        throw new Error('Failed to create task');
      }

      return response.task_id;
    },
    
    async detectWatermark(text: string, key: string, params?: Record<string, any>) {
      if (!this.currentAlgorithm) {
        throw new Error('No algorithm selected');
      }
      const response = await api.watermark.detect({
        text,
        algorithm: this.currentAlgorithm,
        key,
        params,
      });

      if (!response || !response.task_id) {
        throw new Error('Failed to create task');
      }

      return response.task_id;
    },
  },
});

// 模型管理相关接口
export const useModelStore = defineStore('model', {
  state: () => ({
    models: [] as Model[],
    currentModel: null as Model | null,
  }),
  
  actions: {
    async fetchModels() {
      try {
        const models = await api.models.getModels();
        this.models = models;
      } catch (error) {
        console.error('Failed to fetch models:', error);
        throw error;
      }
    },
    
    setCurrentModel(model: Model) {
      this.currentModel = model;
    },
    
    async loadModel(modelId: string) {
      const response = await api.models.loadModel(modelId);
      const taskStore = useTaskStore();
      return new Promise((resolve, reject) => {
        taskStore.startPolling(
          response.task_id,
          (result) => {
            // 更新模型加载状态
            const model = this.models.find((m: Model) => m.id === modelId);
            if (model) {
              model.is_loaded = true;
            }
            resolve(result);
          },
          (error) => reject(new Error(error))
        );
      });
    },
    
    async generateText(modelId: string, prompt: string) {
      const response = await api.models.generateText(modelId, { prompt });
      return response.task_id;
    },
    
    async addModel(modelData: { model_name: string; description: string }) {
      const response = await api.models.addModel(modelData);
      const taskStore = useTaskStore();
      return new Promise((resolve, reject) => {
        taskStore.startPolling(
          response.task_id,
          async (result) => {
            // 重新获取模型列表
            await this.fetchModels();
            resolve(result);
          },
          (error) => reject(new Error(error))
        );
      });
    },

    async deleteModel(modelId: string) {
      await api.models.deleteModel(modelId);
      // 从本地状态中移除模型
      this.models = this.models.filter(model => model.id !== modelId);
    }
  },
});

// 数据集管理相关接口
export const useDatasetStore = defineStore('dataset', {
  state: () => ({
    datasets: [] as Dataset[],
    currentDataset: null as Dataset | null,
  }),
  
  actions: {
    async fetchDatasets() {
      try {
        const datasets = await api.datasets.getDatasets();
        this.datasets = datasets;
      } catch (error) {
        console.error('Failed to fetch datasets:', error);
        throw error;
      }
    },
    
    setCurrentDataset(dataset: Dataset) {
      this.currentDataset = dataset;
    },
    
    async uploadDataset(formData: FormData) {
      const response = await api.datasets.uploadDataset(formData);
      const taskStore = useTaskStore();
      return new Promise((resolve, reject) => {
        taskStore.startPolling(
          response.task_id,
          async (result) => {
            // 重新获取数据集列表
            await this.fetchDatasets();
            resolve(result);
          },
          (error) => reject(new Error(error))
        );
      });
    },
    
    async importFromHuggingFace(params: {
      dataset_name: string;
      description?: string;
    }) {
      const response = await api.datasets.importFromHuggingFace(params);
      const taskStore = useTaskStore();
      return new Promise((resolve, reject) => {
        taskStore.startPolling(
          response.task_id,
          async (result) => {
            // 重新获取数据集列表
            await this.fetchDatasets();
            resolve(result);
          },
          (error) => reject(new Error(error))
        );
      });
    },

    async deleteDataset(datasetId: string) {
      await api.datasets.deleteDataset(datasetId);
      // 从本地状态中移除数据集
      this.datasets = this.datasets.filter(dataset => dataset.id !== datasetId);
    }
  },
});

// 评估相关接口
export const useEvaluateStore = defineStore('evaluate', {
  state: () => ({
    metrics: [] as string[],
    currentMetrics: [] as string[],
    evaluationResults: null as any,
  }),
  
  actions: {
    async evaluateMetrics(data: {
      original_text: string;
      watermarked_text: string;
      algorithm: string;
      key: string;
      metrics: string[];
      params?: Record<string, any>;
    }) {
      const response = await api.evaluate.metrics(data);
      const taskStore = useTaskStore();
      return new Promise((resolve, reject) => {
        taskStore.startPolling(
          response.task_id,
          (result) => {
            this.evaluationResults = result;
            resolve(result);
          },
          (error) => reject(new Error(error))
        );
      });
    },
    
    setCurrentMetrics(metrics: string[]) {
      this.currentMetrics = metrics;
    },
    
    clearResults() {
      this.evaluationResults = null;
    },
  },
});