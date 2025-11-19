/**
 * 通用类型定义
 */

export type MarketType = 'CN' | 'HK' | 'US'

export type Language = 'zh-CN' | 'en-US'

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface ApiResponse<T = unknown> {
  data?: T
  error?: string
  message?: string
}

export interface ApiError {
  error: string
  message: string
  detail?: string
}
