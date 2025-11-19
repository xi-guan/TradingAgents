/**
 * 分析状态管理
 */

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { analysisService, websocketService } from '@/services'
import type { AnalysisTask, StartAnalysisRequest } from '@/types'
import type { AnalysisProgressMessage } from '@/services'

interface AnalysisState {
  currentTask: AnalysisTask | null
  taskHistory: AnalysisTask[]
  isLoading: boolean
  error: string | null

  // Actions
  startAnalysis: (data: StartAnalysisRequest) => Promise<AnalysisTask>
  getTask: (taskId: string) => Promise<void>
  fetchHistory: () => Promise<void>
  deleteTask: (taskId: string) => Promise<void>
  subscribeProgress: (taskId: string) => () => void
  clearError: () => void
}

export const useAnalysisStore = create<AnalysisState>()(
  immer((set, get) => ({
    currentTask: null,
    taskHistory: [],
    isLoading: false,
    error: null,

    startAnalysis: async (data) => {
      set({ isLoading: true, error: null })
      try {
        const task = await analysisService.startAnalysis(data)
        set({
          currentTask: task,
          isLoading: false,
        })

        // 订阅进度更新
        get().subscribeProgress(task.id)

        return task
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : '启动分析失败',
          isLoading: false,
        })
        throw error
      }
    },

    getTask: async (taskId) => {
      set({ isLoading: true, error: null })
      try {
        const task = await analysisService.getAnalysisTask(taskId)
        set({
          currentTask: task,
          isLoading: false,
        })
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : '获取任务失败',
          isLoading: false,
        })
      }
    },

    fetchHistory: async () => {
      set({ isLoading: true, error: null })
      try {
        const history = await analysisService.getAnalysisHistory()
        set({
          taskHistory: history,
          isLoading: false,
        })
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : '获取历史失败',
          isLoading: false,
        })
      }
    },

    deleteTask: async (taskId) => {
      try {
        await analysisService.deleteAnalysisTask(taskId)
        set((state) => {
          state.taskHistory = state.taskHistory.filter((t) => t.id !== taskId)
          if (state.currentTask?.id === taskId) {
            state.currentTask = null
          }
        })
      } catch (error) {
        set({
          error: error instanceof Error ? error.message : '删除任务失败',
        })
      }
    },

    subscribeProgress: (taskId) => {
      return websocketService.subscribe('analysis_progress', (data) => {
        const message = data as AnalysisProgressMessage
        if (message.task_id === taskId) {
          set((state) => {
            if (state.currentTask?.id === taskId) {
              state.currentTask.progress = message.progress
              state.currentTask.status = message.progress >= 100 ? 'completed' : 'running'
            }
          })
        }
      })
    },

    clearError: () => {
      set({ error: null })
    },
  }))
)
