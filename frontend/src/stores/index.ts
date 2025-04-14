import { defineStore } from 'pinia';
import api from '@/api';
import router from '@/router';
import { ElMessage } from 'element-plus';

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
      return api.watermark.embed({
        text,
        algorithm: this.currentAlgorithm,
        key,
        params,
      });
    },
    
    async detectWatermark(text: string, key: string, params?: Record<string, any>) {
      if (!this.currentAlgorithm) {
        throw new Error('No algorithm selected');
      }
      return api.watermark.detect({
        text,
        algorithm: this.currentAlgorithm,
        key,
        params,
      });
    },
  },
});