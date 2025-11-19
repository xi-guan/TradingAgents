/**
 * WebSocket 服务
 */

import { io, type Socket } from 'socket.io-client'
import type { AnalysisProgress } from '@/types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export type WebSocketMessageHandler = (data: unknown) => void

export class WebSocketService {
  private socket: Socket | null = null
  private messageHandlers: Map<string, Set<WebSocketMessageHandler>> = new Map()

  /**
   * 连接 WebSocket
   */
  connect(userId: string, token: string): void {
    if (this.socket?.connected) {
      return
    }

    this.socket = io(`${WS_URL}/api/v1/ws/${userId}`, {
      auth: {
        token,
      },
      transports: ['websocket'],
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })

    this.socket.on('message', (data: unknown) => {
      this.handleMessage(data)
    })

    this.socket.on('error', (error: Error) => {
      console.error('WebSocket error:', error)
    })
  }

  /**
   * 断开 WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.messageHandlers.clear()
  }

  /**
   * 订阅消息
   */
  subscribe(type: string, handler: WebSocketMessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set())
    }
    this.messageHandlers.get(type)?.add(handler)

    // 返回取消订阅函数
    return () => {
      this.messageHandlers.get(type)?.delete(handler)
    }
  }

  /**
   * 发送消息
   */
  send(type: string, data: unknown): void {
    if (this.socket?.connected) {
      this.socket.emit(type, data)
    }
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(data: unknown): void {
    const message = data as { type: string; [key: string]: unknown }
    const handlers = this.messageHandlers.get(message.type)

    if (handlers) {
      for (const handler of handlers) {
        handler(message)
      }
    }
  }
}

// 全局单例
export const websocketService = new WebSocketService()

/**
 * 消息类型定义
 */
export interface AnalysisProgressMessage extends AnalysisProgress {
  type: 'analysis_progress'
}

export interface MarketDataMessage {
  type: 'market_data'
  symbol: string
  market: string
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
}

export interface TradingUpdateMessage {
  type: 'trading_update'
  event: string
  order_id: string
  symbol: string
  side: string
  quantity: number
  price: number
  timestamp: string
}
