/**
 * 头部组件
 */

import { LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined, UserOutlined } from '@ant-design/icons'
import { Avatar, Button, Dropdown, Select, Space, type MenuProps } from 'antd'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, useUiStore } from '@/stores'
import type { Language } from '@/types'

export function Header() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { language, sidebarCollapsed, setLanguage, toggleSidebar } = useUiStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: t('nav.settings'),
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('common.logout'),
      onClick: handleLogout,
    },
  ]

  const handleLanguageChange = (value: Language) => {
    setLanguage(value)
  }

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        height: 64,
      }}
    >
      <Space>
        <Button
          type="text"
          icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={toggleSidebar}
          style={{ fontSize: 16 }}
        />
        <h2 style={{ margin: 0, fontSize: 20 }}>TradingAgents</h2>
      </Space>

      <Space size="middle">
        <Select
          value={language}
          onChange={handleLanguageChange}
          style={{ width: 120 }}
          options={[
            { label: '中文', value: 'zh-CN' },
            { label: 'English', value: 'en-US' },
          ]}
        />

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} />
            <span>{user?.username}</span>
          </Space>
        </Dropdown>
      </Space>
    </header>
  )
}
