/**
 * 认证服务
 */

import apiClient from './api'
import type { LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, User } from '@/types'

export const authService = {
  /**
   * 用户登录
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>('/auth/register', data)
    return response.data
  },

  /**
   * 刷新 Token
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me')
    return response.data
  },

  /**
   * 更新用户信息
   */
  async updateUser(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>('/users/me', data)
    return response.data
  },

  /**
   * 退出登录
   */
  logout(): void {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}
