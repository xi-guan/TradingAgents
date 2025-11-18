/**
 * Axios API 客户端配置
 */

import axios, { type AxiosError, type AxiosInstance, type AxiosResponse } from 'axios'
import type { ApiError, ApiResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建 Axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加 JWT Token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加语言标头
    const language = localStorage.getItem('language') || 'zh-CN'
    config.headers['Accept-Language'] = language

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response
  },
  async (error: AxiosError<ApiError>) => {
    // 处理 401 未授权错误
    if (error.response?.status === 401) {
      // 尝试刷新 Token
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          // 重试原始请求
          if (error.config) {
            error.config.headers.Authorization = `Bearer ${access_token}`
            return apiClient.request(error.config)
          }
        } catch {
          // 刷新失败，清除 Token 并跳转登录
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        // 没有刷新 Token，跳转登录
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient

/**
 * API 错误处理辅助函数
 */
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const apiError = error.response?.data as ApiError | undefined
    return apiError?.message || error.message || '网络错误'
  }
  return '未知错误'
}
