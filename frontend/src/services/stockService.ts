/**
 * 股票数据服务
 */

import apiClient from './api'
import type { MarketType, StockHistoryData, StockInfo, StockQuote, StockSearchResult } from '@/types'

export const stockService = {
  /**
   * 搜索股票
   */
  async searchStocks(query: string): Promise<StockSearchResult[]> {
    const response = await apiClient.get<StockSearchResult[]>('/stocks/search', {
      params: { q: query },
    })
    return response.data
  },

  /**
   * 获取股票详情
   */
  async getStockInfo(symbol: string, market: MarketType): Promise<StockInfo> {
    const response = await apiClient.get<StockInfo>(`/stocks/${symbol}`, {
      params: { market },
    })
    return response.data
  },

  /**
   * 获取实时行情
   */
  async getStockQuote(symbol: string, market: MarketType): Promise<StockQuote> {
    const response = await apiClient.get<StockQuote>(`/stocks/${symbol}/quote`, {
      params: { market },
    })
    return response.data
  },

  /**
   * 获取历史数据
   */
  async getStockHistory(
    symbol: string,
    market: MarketType,
    startDate: string,
    endDate: string
  ): Promise<StockHistoryData[]> {
    const response = await apiClient.get<StockHistoryData[]>(`/stocks/${symbol}/history`, {
      params: { market, start_date: startDate, end_date: endDate },
    })
    return response.data
  },
}
