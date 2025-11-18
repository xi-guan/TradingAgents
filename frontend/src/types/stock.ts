/**
 * 股票相关类型定义
 */

import type { MarketType } from './common'

export interface StockInfo {
  symbol: string
  name: string
  market: MarketType
  full_symbol: string
  industry?: string
  area?: string
  list_date?: string
}

export interface StockQuote {
  symbol: string
  market: MarketType
  price: number
  change: number
  change_percent: number
  volume: number
  amount: number
  open: number
  high: number
  low: number
  close: number
  prev_close: number
  timestamp: string
}

export interface StockHistoryData {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface StockSearchResult {
  symbol: string
  name: string
  market: MarketType
  full_symbol: string
}
