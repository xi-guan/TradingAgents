/**
 * Dashboard 页面
 */

import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  BarChartOutlined,
  LineChartOutlined,
  ShoppingCartOutlined,
} from '@ant-design/icons'
import { Button, Card, Col, Row, Statistic, Table } from 'antd'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores'
import type { ColumnsType } from 'antd/es/table'

interface MarketIndexData {
  key: string
  name: string
  value: number
  change: number
  changePercent: number
}

interface RecentAnalysisData {
  key: string
  symbol: string
  market: string
  status: string
  date: string
}

export function DashboardPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user } = useAuthStore()

  // 模拟市场数据
  const marketIndices: MarketIndexData[] = [
    { key: '1', name: '上证指数', value: 3245.12, change: 32.45, changePercent: 1.01 },
    { key: '2', name: '深证成指', value: 11234.56, change: -45.67, changePercent: -0.40 },
    { key: '3', name: '恒生指数', value: 18234.78, change: 123.45, changePercent: 0.68 },
  ]

  // 模拟最近分析
  const recentAnalysis: RecentAnalysisData[] = [
    { key: '1', symbol: '000001', market: 'CN', status: '已完成', date: '2024-01-15' },
    { key: '2', symbol: '600000', market: 'CN', status: '分析中', date: '2024-01-15' },
    { key: '3', symbol: 'AAPL', market: 'US', status: '已完成', date: '2024-01-14' },
  ]

  const analysisColumns: ColumnsType<RecentAnalysisData> = [
    {
      title: t('analysis.stock_symbol'),
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: t('analysis.market'),
      dataIndex: 'market',
      key: 'market',
      render: (market: string) => t(`market.${market.toLowerCase()}`),
    },
    {
      title: t('common.status'),
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: t('analysis.analysis_date'),
      dataIndex: 'date',
      key: 'date',
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 600 }}>
          {t('dashboard.welcome')}, {user?.username}
        </h1>
        <p style={{ color: '#666', fontSize: 16 }}>{t('dashboard.title')}</p>
      </div>

      {/* 快速操作 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/analysis')}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <LineChartOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              <div style={{ marginLeft: 16 }}>
                <div style={{ fontSize: 16 }}>{t('dashboard.start_analysis')}</div>
                <div style={{ color: '#666', fontSize: 12 }}>分析股票并获取投资建议</div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/market')}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <BarChartOutlined style={{ fontSize: 48, color: '#52c41a' }} />
              <div style={{ marginLeft: 16 }}>
                <div style={{ fontSize: 16 }}>{t('dashboard.view_market')}</div>
                <div style={{ color: '#666', fontSize: 12 }}>查看实时行情和市场数据</div>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/trading')}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <ShoppingCartOutlined style={{ fontSize: 48, color: '#faad14' }} />
              <div style={{ marginLeft: 16 }}>
                <div style={{ fontSize: 16 }}>{t('dashboard.new_order')}</div>
                <div style={{ color: '#666', fontSize: 12 }}>创建模拟交易订单</div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 市场概览 */}
      <Card title={t('dashboard.market_overview')} style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          {marketIndices.map((index) => (
            <Col xs={24} sm={8} key={index.key}>
              <Statistic
                title={index.name}
                value={index.value}
                precision={2}
                valueStyle={{ color: index.change > 0 ? '#3f8600' : '#cf1322' }}
                prefix={index.change > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                suffix={
                  <span style={{ fontSize: 14 }}>
                    {index.changePercent > 0 ? '+' : ''}
                    {index.changePercent.toFixed(2)}%
                  </span>
                }
              />
            </Col>
          ))}
        </Row>
      </Card>

      {/* 最近分析 */}
      <Card
        title={t('dashboard.recent_analysis')}
        extra={
          <Button type="link" onClick={() => navigate('/analysis')}>
            查看全部
          </Button>
        }
      >
        <Table
          columns={analysisColumns}
          dataSource={recentAnalysis}
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  )
}
