/**
 * 交易相关类型定义
 */

import type { MarketType } from './common'

export type OrderSide = 'buy' | 'sell'
export type OrderType = 'market' | 'limit'
export type OrderStatus = 'pending' | 'filled' | 'cancelled' | 'rejected'

export interface TradingAccount {
  id: string
  user_id: string
  account_type: 'paper'
  cash_cny: number
  cash_hkd: number
  cash_usd: number
  created_at: string
  updated_at: string
}

export interface Position {
  id: string
  account_id: string
  symbol: string
  market: MarketType
  quantity: number
  avg_cost: number
  current_price: number
  unrealized_pnl: number
  created_at: string
  updated_at: string
}

export interface Order {
  id: string
  account_id: string
  symbol: string
  market: MarketType
  side: OrderSide
  order_type: OrderType
  quantity: number
  price?: number
  filled_quantity: number
  filled_price?: number
  status: OrderStatus
  filled_at?: string
  created_at: string
}

export interface CreateOrderRequest {
  symbol: string
  market: MarketType
  side: OrderSide
  order_type: OrderType
  quantity: number
  price?: number
}

export interface PortfolioOverview {
  total_value: number
  total_pnl: number
  return_rate: number
  positions_count: number
}
