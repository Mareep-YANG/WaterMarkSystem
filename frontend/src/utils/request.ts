import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ElMessage } from 'element-plus';

const baseURL = 'http://localhost:8000/api/v1';

class Request {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
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
        if (response?.status === 401) {
          // 清除token并跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        
        ElMessage.error(response?.data?.detail || '请求失败');
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

  public post<T = any>(url: string, data?: any): Promise<T> {
    return this.request({ method: 'POST', url, data });
  }

  public put<T = any>(url: string, data?: any): Promise<T> {
    return this.request({ method: 'PUT', url, data });
  }

  public delete<T = any>(url: string): Promise<T> {
    return this.request({ method: 'DELETE', url });
  }
}

export default new Request();