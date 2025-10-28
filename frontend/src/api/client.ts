import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiError } from '@/types/api';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api') {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        // if (typeof window !== 'undefined') {
        //   const token = localStorage.getItem('authToken');
        //   if (token) {
        //     config.headers.Authorization = `Bearer ${token}`;
        //   } 
        // }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response.data;
      },
      (error: AxiosError<ApiError>) => {
        const apiError: ApiError = {
          detail: error.response?.data?.detail || 'An unexpected error occurred',
          statusCode: error.response?.status || 500,
          error: error.response?.data?.error,
          message: error.message
        } 
        return Promise.reject(apiError);
      }
    );
  }

  async get<AxiosResponse>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse> {
    const response = await this.client.get<AxiosResponse>(url, config);
    return response.data;
  }

  // async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  //   const response = await this.client.post<ApiResponse<T>>(url, data, config);
  //   return response.data;
  // }

  // async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  //   const response = await this.client.put<ApiResponse<T>>(url, data, config);
  //   return response.data;
  // }

  // async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  //   const response = await this.client.patch<ApiResponse<T>>(url, data, config);
  //   return response.data;
  // }

  // async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
  //   const response = await this.client.delete<ApiResponse<T>>(url, config);
  //   return response.data;
  // }
}

export const apiClient = new ApiClient();