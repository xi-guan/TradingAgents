import { useState, useEffect } from 'react';
import {
	Card,
	Row,
	Col,
	Statistic,
	Table,
	Button,
	Modal,
	Form,
	Input,
	Select,
	InputNumber,
	message,
	Tabs,
	Tag,
	Space,
} from 'antd';
import {
	DollarOutlined,
	PlusOutlined,
	LineChartOutlined,
	RiseOutlined,
	FallOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import { tradingService } from '../../services/tradingService';
import type {
	TradingAccount,
	Position,
	Order,
	OrderCreate,
} from '../../types/trading';

export default function Trading() {
	const { t } = useTranslation();
	const [account, setAccount] = useState<TradingAccount | null>(null);
	const [positions, setPositions] = useState<Position[]>([]);
	const [orders, setOrders] = useState<Order[]>([]);
	const [loading, setLoading] = useState(false);
	const [orderModalVisible, setOrderModalVisible] = useState(false);
	const [orderForm] = Form.useForm();

	// 加载账户数据
	const loadAccountData = async () => {
		setLoading(true);
		try {
			const accountData = await tradingService.getAccount();
			setAccount(accountData);

			const [positionsData, ordersData] = await Promise.all([
				tradingService.getPositions(),
				tradingService.getOrders(),
			]);

			setPositions(positionsData);
			setOrders(ordersData);
		} catch (error) {
			message.error(t('trading.loadFailed'));
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		loadAccountData();
	}, []);

	// 创建订单
	const handleCreateOrder = async (values: OrderCreate) => {
		try {
			await tradingService.createOrder(values);
			message.success(t('trading.orderCreated'));
			setOrderModalVisible(false);
			orderForm.resetFields();
			await loadAccountData();
		} catch (error) {
			message.error(t('trading.orderFailed'));
		}
	};

	// 取消订单
	const handleCancelOrder = async (orderId: string) => {
		try {
			await tradingService.cancelOrder(orderId);
			message.success(t('trading.orderCancelled'));
			await loadAccountData();
		} catch (error) {
			message.error(t('trading.cancelFailed'));
		}
	};

	// 持仓列配置
	const positionColumns: ColumnsType<Position> = [
		{
			title: t('trading.symbol'),
			dataIndex: ['stock', 'symbol'],
			key: 'symbol',
		},
		{
			title: t('trading.name'),
			dataIndex: ['stock', 'name'],
			key: 'name',
		},
		{
			title: t('trading.quantity'),
			dataIndex: 'quantity',
			key: 'quantity',
			align: 'right',
		},
		{
			title: t('trading.avgCost'),
			dataIndex: 'avg_cost',
			key: 'avg_cost',
			align: 'right',
			render: (value: number) => value.toFixed(2),
		},
		{
			title: t('trading.currentPrice'),
			dataIndex: 'current_price',
			key: 'current_price',
			align: 'right',
			render: (value: number) => value?.toFixed(2) || '-',
		},
		{
			title: t('trading.marketValue'),
			dataIndex: 'market_value',
			key: 'market_value',
			align: 'right',
			render: (value: number) => value?.toFixed(2) || '-',
		},
		{
			title: t('trading.profitLoss'),
			dataIndex: 'profit_loss',
			key: 'profit_loss',
			align: 'right',
			render: (value: number, record: Position) => (
				<span style={{ color: value >= 0 ? '#3f8600' : '#cf1322' }}>
					{value >= 0 ? '+' : ''}
					{value?.toFixed(2) || '-'} ({record.profit_loss_rate?.toFixed(2) || 0}%)
				</span>
			),
		},
		{
			title: t('common.action'),
			key: 'action',
			render: (_, record) => (
				<Space>
					<Button
						type="link"
						size="small"
						onClick={() => {
							orderForm.setFieldsValue({
								symbol: record.stock.symbol,
								market: record.stock.market,
								side: 'SELL',
								quantity: record.quantity,
							});
							setOrderModalVisible(true);
						}}
					>
						{t('trading.sell')}
					</Button>
				</Space>
			),
		},
	];

	// 订单列配置
	const orderColumns: ColumnsType<Order> = [
		{
			title: t('trading.createTime'),
			dataIndex: 'created_at',
			key: 'created_at',
			render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
		},
		{
			title: t('trading.symbol'),
			dataIndex: ['stock', 'symbol'],
			key: 'symbol',
		},
		{
			title: t('trading.side'),
			dataIndex: 'side',
			key: 'side',
			render: (value: string) => (
				<Tag color={value === 'BUY' ? 'green' : 'red'}>
					{value === 'BUY' ? t('trading.buy') : t('trading.sell')}
				</Tag>
			),
		},
		{
			title: t('trading.orderType'),
			dataIndex: 'order_type',
			key: 'order_type',
			render: (value: string) => t(`trading.${value.toLowerCase()}`),
		},
		{
			title: t('trading.quantity'),
			dataIndex: 'quantity',
			key: 'quantity',
			align: 'right',
		},
		{
			title: t('trading.price'),
			dataIndex: 'price',
			key: 'price',
			align: 'right',
			render: (value: number) => value?.toFixed(2) || t('trading.market'),
		},
		{
			title: t('trading.status'),
			dataIndex: 'status',
			key: 'status',
			render: (value: string) => {
				const colorMap: Record<string, string> = {
					PENDING: 'blue',
					FILLED: 'green',
					CANCELLED: 'red',
					REJECTED: 'volcano',
				};
				return <Tag color={colorMap[value]}>{t(`trading.${value.toLowerCase()}`)}</Tag>;
			},
		},
		{
			title: t('common.action'),
			key: 'action',
			render: (_, record) => (
				<Space>
					{record.status === 'PENDING' && (
						<Button
							type="link"
							size="small"
							danger
							onClick={() => handleCancelOrder(record.id)}
						>
							{t('trading.cancel')}
						</Button>
					)}
				</Space>
			),
		},
	];

	return (
		<div style={{ padding: '24px' }}>
			{/* 账户概览 */}
			<Card
				title={t('trading.accountOverview')}
				extra={
					<Button type="primary" icon={<PlusOutlined />} onClick={() => setOrderModalVisible(true)}>
						{t('trading.newOrder')}
					</Button>
				}
				loading={loading}
				style={{ marginBottom: 24 }}
			>
				<Row gutter={16}>
					<Col span={6}>
						<Statistic
							title={t('trading.totalValue')}
							value={account?.total_value || 0}
							precision={2}
							prefix={<DollarOutlined />}
							suffix={account?.currency || 'CNY'}
						/>
					</Col>
					<Col span={6}>
						<Statistic
							title={t('trading.cashBalance')}
							value={account?.cash_balance || 0}
							precision={2}
							suffix={account?.currency || 'CNY'}
						/>
					</Col>
					<Col span={6}>
						<Statistic
							title={t('trading.totalProfitLoss')}
							value={account?.total_profit_loss || 0}
							precision={2}
							valueStyle={{
								color: (account?.total_profit_loss || 0) >= 0 ? '#3f8600' : '#cf1322',
							}}
							prefix={
								(account?.total_profit_loss || 0) >= 0 ? (
									<RiseOutlined />
								) : (
									<FallOutlined />
								)
							}
						/>
					</Col>
					<Col span={6}>
						<Statistic
							title={t('trading.totalReturnRate')}
							value={account?.total_return_rate || 0}
							precision={2}
							suffix="%"
							valueStyle={{
								color: (account?.total_return_rate || 0) >= 0 ? '#3f8600' : '#cf1322',
							}}
						/>
					</Col>
				</Row>
			</Card>

			{/* 持仓和订单 */}
			<Card>
				<Tabs
					items={[
						{
							key: 'positions',
							label: t('trading.positions'),
							children: (
								<Table
									columns={positionColumns}
									dataSource={positions}
									rowKey="id"
									loading={loading}
									pagination={{ pageSize: 10 }}
								/>
							),
						},
						{
							key: 'orders',
							label: t('trading.orders'),
							children: (
								<Table
									columns={orderColumns}
									dataSource={orders}
									rowKey="id"
									loading={loading}
									pagination={{ pageSize: 10 }}
								/>
							),
						},
					]}
				/>
			</Card>

			{/* 下单模态框 */}
			<Modal
				title={t('trading.newOrder')}
				open={orderModalVisible}
				onCancel={() => {
					setOrderModalVisible(false);
					orderForm.resetFields();
				}}
				footer={null}
			>
				<Form form={orderForm} layout="vertical" onFinish={handleCreateOrder}>
					<Form.Item
						label={t('trading.symbol')}
						name="symbol"
						rules={[{ required: true, message: t('trading.symbolRequired') }]}
					>
						<Input placeholder={t('trading.symbolPlaceholder')} />
					</Form.Item>

					<Form.Item
						label={t('trading.market')}
						name="market"
						rules={[{ required: true, message: t('trading.marketRequired') }]}
					>
						<Select placeholder={t('trading.selectMarket')}>
							<Select.Option value="CN">{t('market.cnMarket')}</Select.Option>
							<Select.Option value="HK">{t('market.hkMarket')}</Select.Option>
							<Select.Option value="US">{t('market.usMarket')}</Select.Option>
						</Select>
					</Form.Item>

					<Form.Item
						label={t('trading.side')}
						name="side"
						rules={[{ required: true, message: t('trading.sideRequired') }]}
					>
						<Select placeholder={t('trading.selectSide')}>
							<Select.Option value="BUY">{t('trading.buy')}</Select.Option>
							<Select.Option value="SELL">{t('trading.sell')}</Select.Option>
						</Select>
					</Form.Item>

					<Form.Item
						label={t('trading.orderType')}
						name="order_type"
						initialValue="MARKET"
						rules={[{ required: true }]}
					>
						<Select>
							<Select.Option value="MARKET">{t('trading.market')}</Select.Option>
							<Select.Option value="LIMIT">{t('trading.limit')}</Select.Option>
						</Select>
					</Form.Item>

					<Form.Item
						label={t('trading.quantity')}
						name="quantity"
						rules={[
							{ required: true, message: t('trading.quantityRequired') },
							{ type: 'number', min: 1, message: t('trading.quantityMin') },
						]}
					>
						<InputNumber
							style={{ width: '100%' }}
							placeholder={t('trading.quantityPlaceholder')}
							min={1}
						/>
					</Form.Item>

					<Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.order_type !== currentValues.order_type}>
						{({ getFieldValue }) =>
							getFieldValue('order_type') === 'LIMIT' ? (
								<Form.Item
									label={t('trading.price')}
									name="price"
									rules={[
										{ required: true, message: t('trading.priceRequired') },
										{ type: 'number', min: 0.01, message: t('trading.priceMin') },
									]}
								>
									<InputNumber
										style={{ width: '100%' }}
										placeholder={t('trading.pricePlaceholder')}
										min={0.01}
										precision={2}
									/>
								</Form.Item>
							) : null
						}
					</Form.Item>

					<Form.Item label={t('trading.notes')} name="notes">
						<Input.TextArea placeholder={t('trading.notesPlaceholder')} rows={3} />
					</Form.Item>

					<Form.Item>
						<Space style={{ width: '100%', justifyContent: 'flex-end' }}>
							<Button
								onClick={() => {
									setOrderModalVisible(false);
									orderForm.resetFields();
								}}
							>
								{t('common.cancel')}
							</Button>
							<Button type="primary" htmlType="submit">
								{t('common.submit')}
							</Button>
						</Space>
					</Form.Item>
				</Form>
			</Modal>
		</div>
	);
}
