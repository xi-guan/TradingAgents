/**
 * UI 状态管理
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import i18n from '@/utils/i18n'
import type { Language } from '@/types'

interface UiState {
  language: Language
  theme: 'light' | 'dark'
  sidebarCollapsed: boolean

  // Actions
  setLanguage: (language: Language) => void
  setTheme: (theme: 'light' | 'dark') => void
  toggleSidebar: () => void
}

export const useUiStore = create<UiState>()(
  persist(
    immer((set) => ({
      language: 'zh-CN',
      theme: 'light',
      sidebarCollapsed: false,

      setLanguage: (language) => {
        set({ language })
        localStorage.setItem('language', language)
        i18n.changeLanguage(language).catch((error) => {
          console.error('Failed to change language:', error)
        })
      },

      setTheme: (theme) => {
        set({ theme })
      },

      toggleSidebar: () => {
        set((state) => {
          state.sidebarCollapsed = !state.sidebarCollapsed
        })
      },
    })),
    {
      name: 'ui-storage',
    }
  )
)
