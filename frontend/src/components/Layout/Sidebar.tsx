/**
 * 侧边栏组件
 */

import {
  BarChartOutlined,
  DashboardOutlined,
  FileTextOutlined,
  LineChartOutlined,
  SettingOutlined,
  ShoppingCartOutlined,
  StockOutlined,
} from '@ant-design/icons'
import { Menu } from 'antd'
import { useTranslation } from 'react-i18next'
import { useLocation, useNavigate } from 'react-router-dom'
import { useUiStore } from '@/stores'

export function Sidebar() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const { sidebarCollapsed } = useUiStore()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: t('nav.dashboard'),
    },
    {
      key: '/analysis',
      icon: <LineChartOutlined />,
      label: t('nav.analysis'),
    },
    {
      key: '/market',
      icon: <StockOutlined />,
      label: t('nav.market'),
    },
    {
      key: '/trading',
      icon: <ShoppingCartOutlined />,
      label: t('nav.trading'),
    },
    {
      key: '/portfolio',
      icon: <BarChartOutlined />,
      label: t('nav.portfolio'),
    },
    {
      key: '/reports',
      icon: <FileTextOutlined />,
      label: t('nav.reports'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: t('nav.settings'),
    },
  ]

  return (
    <aside
      style={{
        width: sidebarCollapsed ? 80 : 200,
        background: '#001529',
        transition: 'width 0.2s',
      }}
    >
      <Menu
        mode="inline"
        theme="dark"
        selectedKeys={[location.pathname]}
        inlineCollapsed={sidebarCollapsed}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
        style={{ height: '100%', borderRight: 0 }}
      />
    </aside>
  )
}
