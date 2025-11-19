/**
 * 认证状态管理
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { authService } from '@/services'
import type { LoginRequest, RegisterRequest, User } from '@/types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
  updateUser: (data: Partial<User>) => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authService.login(data)
          localStorage.setItem('access_token', response.access_token)
          localStorage.setItem('refresh_token', response.refresh_token)
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '登录失败',
            isLoading: false,
          })
          throw error
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authService.register(data)
          set({
            user: response.user,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '注册失败',
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        authService.logout()
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        })
      },

      fetchCurrentUser: async () => {
        set({ isLoading: true })
        try {
          const user = await authService.getCurrentUser()
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          })
        }
      },

      updateUser: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const user = await authService.updateUser(data)
          set({
            user,
            isLoading: false,
          })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : '更新失败',
            isLoading: false,
          })
          throw error
        }
      },

      clearError: () => {
        set({ error: null })
      },
    })),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
