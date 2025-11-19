/**
 * 股票分析页面
 */

import { Button, Card, Col, DatePicker, Form, Input, message, Progress, Row, Select } from 'antd'
import dayjs from 'dayjs'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAnalysisStore } from '@/stores'
import type { AnalysisDepth, MarketType, StartAnalysisRequest } from '@/types'

export function AnalysisPage() {
  const { t } = useTranslation()
  const { startAnalysis, currentTask, isLoading } = useAnalysisStore()
  const [form] = Form.useForm()
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleSubmit = async (values: {
    symbol: string
    market: MarketType
    analysis_date?: string
    depth: AnalysisDepth
  }) => {
    try {
      setIsAnalyzing(true)

      const request: StartAnalysisRequest = {
        symbol: values.symbol,
        market: values.market,
        analysis_date: values.analysis_date || dayjs().format('YYYY-MM-DD'),
        depth: values.depth,
      }

      await startAnalysis(request)
      message.success(t('analysis.start_analysis'))
    } catch (error) {
      message.error(error instanceof Error ? error.message : '启动分析失败')
      setIsAnalyzing(false)
    }
  }

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 600, marginBottom: 24 }}>
        {t('analysis.title')}
      </h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title={t('analysis.start_analysis')}>
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                market: 'CN' as MarketType,
                depth: 3 as AnalysisDepth,
              }}
              onFinish={handleSubmit}
            >
              <Form.Item
                label={t('analysis.stock_symbol')}
                name="symbol"
                rules={[{ required: true, message: '请输入股票代码' }]}
              >
                <Input placeholder="例如: 000001" size="large" />
              </Form.Item>

              <Form.Item
                label={t('analysis.market')}
                name="market"
                rules={[{ required: true }]}
              >
                <Select size="large">
                  <Select.Option value="CN">{t('market.cn')}</Select.Option>
                  <Select.Option value="HK">{t('market.hk')}</Select.Option>
                  <Select.Option value="US">{t('market.us')}</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label={t('analysis.analysis_date')} name="analysis_date">
                <DatePicker
                  style={{ width: '100%' }}
                  size="large"
                  format="YYYY-MM-DD"
                  disabledDate={(current) => current && current > dayjs().endOf('day')}
                />
              </Form.Item>

              <Form.Item label={t('analysis.depth')} name="depth">
                <Select size="large">
                  <Select.Option value={1}>{t('analysis.depth_quick')}</Select.Option>
                  <Select.Option value={2}>{t('analysis.depth_basic')}</Select.Option>
                  <Select.Option value={3}>{t('analysis.depth_standard')}</Select.Option>
                  <Select.Option value={4}>{t('analysis.depth_deep')}</Select.Option>
                  <Select.Option value={5}>{t('analysis.depth_comprehensive')}</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={isLoading || isAnalyzing}
                  block
                >
                  {t('analysis.start_analysis')}
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          {isAnalyzing && currentTask ? (
            <Card title={t('analysis.progress')}>
              <Progress
                percent={currentTask.progress}
                status={currentTask.status === 'failed' ? 'exception' : 'active'}
              />
              <div style={{ marginTop: 16 }}>
                <p>
                  <strong>股票:</strong> {currentTask.symbol} ({currentTask.market})
                </p>
                <p>
                  <strong>状态:</strong> {currentTask.status}
                </p>
              </div>
            </Card>
          ) : (
            <Card
              title={t('analysis.result')}
              style={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <div style={{ textAlign: 'center', color: '#999' }}>
                <p style={{ fontSize: 16 }}>请先启动股票分析</p>
                <p>分析结果将在这里显示</p>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  )
}
