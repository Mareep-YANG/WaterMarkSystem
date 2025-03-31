import { defineStore } from 'pinia';
import api from '@/api';

interface UserState {
  token: string | null;
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
    profile: null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.profile,
  },
  
  actions: {
    setToken(token: string) {
      this.token = token;
      localStorage.setItem('token', token);
    },
    
    clearToken() {
      this.token = null;
      localStorage.removeItem('token');
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
        this.setToken(response.token); 
        await this.fetchProfile();
      } catch (error) {
        console.error('登录失败:', error);
        throw error;
      }
    },
    
    async logout() {
      this.clearToken();
      this.profile = null;
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