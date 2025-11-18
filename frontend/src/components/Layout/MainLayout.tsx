/**
 * 主布局组件
 */

import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function MainLayout() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout>
        <Sidebar />
        <Layout>
          <Header />
          <Layout.Content
            style={{
              padding: 24,
              background: '#f0f2f5',
              minHeight: 'calc(100vh - 64px)',
            }}
          >
            <Outlet />
          </Layout.Content>
        </Layout>
      </Layout>
    </Layout>
  )
}
