/**
 * 登录页面
 */

import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { Button, Card, Checkbox, Form, Input, message } from 'antd'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores'
import type { LoginRequest } from '@/types'

export function LoginPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login, isAuthenticated, isLoading, error, clearError } = useAuthStore()
  const [form] = Form.useForm()

  // 如果已登录，跳转到 Dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  // 显示错误消息
  useEffect(() => {
    if (error) {
      message.error(error)
      clearError()
    }
  }, [error, clearError])

  const handleSubmit = async (values: LoginRequest & { remember: boolean }) => {
    try {
      await login({
        username: values.username,
        password: values.password,
      })
      message.success(t('auth.login_success'))
      navigate('/dashboard')
    } catch {
      // 错误已在 effect 中处理
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 600 }}>{t('auth.login_title')}</h1>
          <p style={{ color: '#666' }}>TradingAgents Web Platform</p>
        </div>

        <Form
          form={form}
          name="login"
          initialValues={{ remember: true }}
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: t('auth.username') }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder={t('auth.username')}
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: t('auth.password') }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={t('auth.password')}
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>{t('auth.remember_me')}</Checkbox>
              </Form.Item>
              <a href="/forgot-password">{t('auth.forgot_password')}</a>
            </div>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              loading={isLoading}
              block
            >
              {t('common.login')}
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            {t('auth.no_account')}{' '}
            <a href="/register">{t('common.register')}</a>
          </div>
        </Form>
      </Card>
    </div>
  )
}
