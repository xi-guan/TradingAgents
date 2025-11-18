/**
 * 分析服务
 */

import apiClient from './api'
import type { AnalysisTask, StartAnalysisRequest } from '@/types'

export const analysisService = {
  /**
   * 开始分析
   */
  async startAnalysis(data: StartAnalysisRequest): Promise<AnalysisTask> {
    const response = await apiClient.post<AnalysisTask>('/analysis/start', data)
    return response.data
  },

  /**
   * 获取分析任务详情
   */
  async getAnalysisTask(taskId: string): Promise<AnalysisTask> {
    const response = await apiClient.get<AnalysisTask>(`/analysis/${taskId}`)
    return response.data
  },

  /**
   * 获取分析结果
   */
  async getAnalysisResult(taskId: string): Promise<AnalysisTask> {
    const response = await apiClient.get<AnalysisTask>(`/analysis/${taskId}/result`)
    return response.data
  },

  /**
   * 获取分析历史
   */
  async getAnalysisHistory(page = 1, pageSize = 20): Promise<AnalysisTask[]> {
    const response = await apiClient.get<AnalysisTask[]>('/analysis/history', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  /**
   * 删除分析任务
   */
  async deleteAnalysisTask(taskId: string): Promise<void> {
    await apiClient.delete(`/analysis/${taskId}`)
  },
}
