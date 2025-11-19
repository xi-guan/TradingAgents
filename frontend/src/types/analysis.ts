/**
 * 分析相关类型定义
 */

import type { MarketType } from './common'

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed'

export type AnalysisDepth = 1 | 2 | 3 | 4 | 5

export interface AnalysisTask {
  id: string
  user_id: string
  symbol: string
  market: MarketType
  analysis_date: string
  depth: AnalysisDepth
  status: AnalysisStatus
  progress: number
  result?: AnalysisResult
  error_message?: string
  created_at: string
  updated_at: string
}

export interface AnalysisResult {
  symbol: string
  market: MarketType
  fundamental?: FundamentalAnalysis
  technical?: TechnicalAnalysis
  sentiment?: SentimentAnalysis
  news?: NewsAnalysis
  recommendation: Recommendation
  risk_assessment: RiskAssessment
}

export interface FundamentalAnalysis {
  summary: string
  metrics: {
    pe_ratio?: number
    pb_ratio?: number
    roe?: number
    gross_margin?: number
    [key: string]: number | undefined
  }
  analysis: string
}

export interface TechnicalAnalysis {
  summary: string
  indicators: {
    [key: string]: number
  }
  signals: string[]
  analysis: string
}

export interface SentimentAnalysis {
  summary: string
  score: number
  analysis: string
}

export interface NewsAnalysis {
  summary: string
  news_items: NewsItem[]
  analysis: string
}

export interface NewsItem {
  title: string
  source: string
  publish_time: string
  url?: string
  sentiment?: number
}

export interface Recommendation {
  action: 'STRONG_BUY' | 'BUY' | 'NEUTRAL' | 'SELL' | 'STRONG_SELL'
  confidence: number
  target_price?: number
  stop_loss?: number
  reasoning: string
}

export interface RiskAssessment {
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  risk_factors: string[]
  mitigation_strategies: string[]
}

export interface AnalysisProgress {
  task_id: string
  progress: number
  stage: string
  message: string
  timestamp: string
}

export interface StartAnalysisRequest {
  symbol: string
  market: MarketType
  analysis_date?: string
  depth?: AnalysisDepth
}
