import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/stores';
import router from '@/router'; 

const baseURL = '/api/v1';

class Request {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL,
      timeout: 30000, // 30秒超时
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // 允许跨域携带凭证
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const userStore = useUserStore();
        if (userStore.token) { 
          config.headers.Authorization = `Bearer ${userStore.token}`;
        }
        // 添加时间戳防止缓存
        if (config.method === 'get') {
          config.params = {
            ...config.params,
            _t: new Date().getTime()
          };
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response.data;
      },
      (error) => {
        const { response } = error;
        const userStore = useUserStore();

        if (response?.status === 401) {
          userStore.logout();
          router.push({
            path: '/login',
            query: { redirect: router.currentRoute.value.fullPath },
          });
          ElMessage.error('会话已过期，请重新登录');
        } else if (response?.status === 504) {
          ElMessage.error('请求超时，请稍后重试');
        } else if (!response) {
          ElMessage.error('网络错误，请检查网络连接');
        }
        return Promise.reject(error);
      }
    );
  }

  public async request<T = any>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.request<T>(config);
      return response as T;
    } catch (error) {
      return Promise.reject(error);
    }
  }

  public get<T = any>(url: string, params?: any): Promise<T> {
    return this.request({ method: 'GET', url, params });
  }

  public post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request({ method: 'POST', url, data, ...config });
  }

  public put<T = any>(url: string, data?: any): Promise<T> {
    return this.request({ method: 'PUT', url, data });
  }

  public delete<T = any>(url: string): Promise<T> {
    return this.request({ method: 'DELETE', url });
  }
  public login<T = any>(username: string, password: string): Promise<T> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    return this.request({
      method: 'POST',
      url: '/auth/login',
      data: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  }
}

export default new Request();