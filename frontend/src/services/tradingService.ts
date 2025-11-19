import { apiClient } from './api';
import type {
	TradingAccount,
	Position,
	Order,
	OrderCreate,
} from '../types/trading';

export const tradingService = {
	/**
	 * 获取交易账户信息
	 */
	async getAccount(): Promise<TradingAccount> {
		const response = await apiClient.get('/trading/account');
		return response.data;
	},

	/**
	 * 创建交易账户
	 */
	async createAccount(data: {
		name: string;
		market: string;
		initial_capital: number;
	}): Promise<TradingAccount> {
		const response = await apiClient.post('/trading/account', data);
		return response.data;
	},

	/**
	 * 获取持仓列表
	 */
	async getPositions(): Promise<Position[]> {
		const response = await apiClient.get('/trading/positions');
		return response.data;
	},

	/**
	 * 获取订单列表
	 */
	async getOrders(status?: string): Promise<Order[]> {
		const response = await apiClient.get('/trading/orders', {
			params: { status },
		});
		return response.data;
	},

	/**
	 * 创建订单
	 */
	async createOrder(data: OrderCreate): Promise<Order> {
		const response = await apiClient.post('/trading/orders', data);
		return response.data;
	},

	/**
	 * 取消订单
	 */
	async cancelOrder(orderId: string): Promise<void> {
		await apiClient.delete(`/trading/orders/${orderId}`);
	},

	/**
	 * 获取订单详情
	 */
	async getOrder(orderId: string): Promise<Order> {
		const response = await apiClient.get(`/trading/orders/${orderId}`);
		return response.data;
	},
};
