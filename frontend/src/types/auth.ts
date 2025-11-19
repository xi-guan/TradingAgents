/**
 * 认证相关类型定义
 */

export interface User {
  id: string
  username: string
  email: string
  preferred_language: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  preferred_language?: string
}

export interface RegisterResponse {
  user: User
  message: string
}
