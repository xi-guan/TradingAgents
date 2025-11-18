/**
 * 应用主组件
 */

import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { MainLayout } from '@/components/Layout'
import { AnalysisPage } from '@/pages/Analysis'
import { DashboardPage } from '@/pages/Dashboard'
import { LoginPage } from '@/pages/Login'
import { useAuthStore, useUiStore } from '@/stores'
import { websocketService } from '@/services'

// 设置 dayjs 语言
dayjs.locale('zh-cn')

function App() {
  const { language } = useUiStore()
  const { isAuthenticated, user, fetchCurrentUser } = useAuthStore()

  // 初始化时获取当前用户
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token && !user) {
      fetchCurrentUser().catch(() => {
        // 忽略错误，让用户重新登录
      })
    }
  }, [user, fetchCurrentUser])

  // 连接 WebSocket
  useEffect(() => {
    if (isAuthenticated && user) {
      const token = localStorage.getItem('access_token')
      if (token) {
        websocketService.connect(user.id, token)
      }

      return () => {
        websocketService.disconnect()
      }
    }
  }, [isAuthenticated, user])

  return (
    <ConfigProvider locale={language === 'zh-CN' ? zhCN : enUS}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* 受保护的路由 */}
          {isAuthenticated ? (
            <Route element={<MainLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/market" element={<div>Market Page (待实现)</div>} />
              <Route path="/trading" element={<div>Trading Page (待实现)</div>} />
              <Route path="/portfolio" element={<div>Portfolio Page (待实现)</div>} />
              <Route path="/reports" element={<div>Reports Page (待实现)</div>} />
              <Route path="/settings" element={<div>Settings Page (待实现)</div>} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Route>
          ) : (
            <Route path="*" element={<Navigate to="/login" replace />} />
          )}
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
