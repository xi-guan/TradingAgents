import { useState } from 'react';
import {
	Card,
	Input,
	Select,
	Row,
	Col,
	Table,
	Statistic,
	Tag,
	Space,
	Button,
	DatePicker,
	Spin,
} from 'antd';
import {
	SearchOutlined,
	LineChartOutlined,
	RiseOutlined,
	FallOutlined,
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { ColumnsType } from 'antd/es/table';
import dayjs, { type Dayjs } from 'dayjs';
import ReactECharts from 'echarts-for-react';
import { stockService } from '../../services/stockService';
import type { Stock, StockQuote, StockHistory } from '../../types/stock';

const { RangePicker } = DatePicker;

export default function Market() {
	const { t } = useTranslation();
	const [searchQuery, setSearchQuery] = useState('');
	const [selectedMarket, setSelectedMarket] = useState<string>('');
	const [searchResults, setSearchResults] = useState<Stock[]>([]);
	const [searching, setSearching] = useState(false);
	const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
	const [quote, setQuote] = useState<StockQuote | null>(null);
	const [history, setHistory] = useState<StockHistory[]>([]);
	const [loadingQuote, setLoadingQuote] = useState(false);
	const [loadingHistory, setLoadingHistory] = useState(false);
	const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
		dayjs().subtract(30, 'day'),
		dayjs(),
	]);

	// 搜索股票
	const handleSearch = async () => {
		if (!searchQuery.trim()) return;

		setSearching(true);
		try {
			const results = await stockService.searchStocks(
				searchQuery,
				selectedMarket || undefined
			);
			setSearchResults(results);
		} catch (error) {
			console.error('Search failed:', error);
		} finally {
			setSearching(false);
		}
	};

	// 选择股票
	const handleSelectStock = async (stock: Stock) => {
		setSelectedStock(stock);
		await Promise.all([fetchQuote(stock), fetchHistory(stock)]);
	};

	// 获取实时行情
	const fetchQuote = async (stock: Stock) => {
		setLoadingQuote(true);
		try {
			const quoteData = await stockService.getQuote(stock.symbol, stock.market);
			setQuote(quoteData);
		} catch (error) {
			console.error('Failed to fetch quote:', error);
		} finally {
			setLoadingQuote(false);
		}
	};

	// 获取历史数据
	const fetchHistory = async (stock: Stock) => {
		setLoadingHistory(true);
		try {
			const historyData = await stockService.getHistory(
				stock.symbol,
				stock.market,
				dateRange[0].format('YYYY-MM-DD'),
				dateRange[1].format('YYYY-MM-DD')
			);
			setHistory(historyData);
		} catch (error) {
			console.error('Failed to fetch history:', error);
		} finally {
			setLoadingHistory(false);
		}
	};

	// 刷新行情
	const handleRefreshQuote = () => {
		if (selectedStock) {
			fetchQuote(selectedStock);
		}
	};

	// 日期范围变化
	const handleDateRangeChange = (dates: null | [Dayjs | null, Dayjs | null]) => {
		if (dates && dates[0] && dates[1]) {
			setDateRange([dates[0], dates[1]]);
			if (selectedStock) {
				fetchHistory(selectedStock);
			}
		}
	};

	// K线图配置
	const getChartOption = () => {
		if (!history.length) return {};

		const dates = history.map((item) => item.timestamp.split('T')[0]);
		const values = history.map((item) => [
			item.open,
			item.close,
			item.low,
			item.high,
		]);

		return {
			title: {
				text: `${selectedStock?.name} (${selectedStock?.symbol})`,
				left: 'center',
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross',
				},
			},
			grid: {
				left: '10%',
				right: '10%',
				bottom: '15%',
			},
			xAxis: {
				type: 'category',
				data: dates,
				scale: true,
				boundaryGap: false,
				axisLine: { onZero: false },
				splitLine: { show: false },
				min: 'dataMin',
				max: 'dataMax',
			},
			yAxis: {
				scale: true,
				splitArea: {
					show: true,
				},
			},
			dataZoom: [
				{
					type: 'inside',
					start: 0,
					end: 100,
				},
				{
					show: true,
					type: 'slider',
					top: '90%',
					start: 0,
					end: 100,
				},
			],
			series: [
				{
					name: t('market.kline'),
					type: 'candlestick',
					data: values,
					itemStyle: {
						color: '#ec0000',
						color0: '#00da3c',
						borderColor: '#8A0000',
						borderColor0: '#008F28',
					},
				},
			],
		};
	};

	// 搜索结果列配置
	const searchColumns: ColumnsType<Stock> = [
		{
			title: t('market.symbol'),
			dataIndex: 'symbol',
			key: 'symbol',
			width: 120,
		},
		{
			title: t('market.name'),
			dataIndex: 'name',
			key: 'name',
		},
		{
			title: t('market.market'),
			dataIndex: 'market',
			key: 'market',
			width: 80,
			render: (market: string) => (
				<Tag color={market === 'CN' ? 'blue' : market === 'HK' ? 'purple' : 'green'}>
					{market}
				</Tag>
			),
		},
		{
			title: t('market.sector'),
			dataIndex: 'sector',
			key: 'sector',
		},
		{
			title: t('common.action'),
			key: 'action',
			width: 100,
			render: (_, record) => (
				<Button
					type="link"
					icon={<LineChartOutlined />}
					onClick={() => handleSelectStock(record)}
				>
					{t('market.viewChart')}
				</Button>
			),
		},
	];

	return (
		<div style={{ padding: '24px' }}>
			{/* 搜索区域 */}
			<Card style={{ marginBottom: 24 }}>
				<Space.Compact style={{ width: '100%' }}>
					<Select
						style={{ width: 120 }}
						placeholder={t('market.allMarkets')}
						value={selectedMarket}
						onChange={setSelectedMarket}
						allowClear
					>
						<Select.Option value="CN">{t('market.cnMarket')}</Select.Option>
						<Select.Option value="HK">{t('market.hkMarket')}</Select.Option>
						<Select.Option value="US">{t('market.usMarket')}</Select.Option>
					</Select>
					<Input
						placeholder={t('market.searchPlaceholder')}
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						onPressEnter={handleSearch}
						prefix={<SearchOutlined />}
					/>
					<Button type="primary" onClick={handleSearch} loading={searching}>
						{t('common.search')}
					</Button>
				</Space.Compact>
			</Card>

			<Row gutter={[24, 24]}>
				{/* 搜索结果 */}
				<Col span={24}>
					<Card title={t('market.searchResults')}>
						<Table
							columns={searchColumns}
							dataSource={searchResults}
							rowKey="symbol"
							loading={searching}
							pagination={{ pageSize: 10 }}
						/>
					</Card>
				</Col>

				{/* 实时行情 */}
				{selectedStock && (
					<>
						<Col span={24}>
							<Card
								title={`${selectedStock.name} (${selectedStock.symbol})`}
								extra={
									<Button onClick={handleRefreshQuote} loading={loadingQuote}>
										{t('market.refresh')}
									</Button>
								}
							>
								<Spin spinning={loadingQuote}>
									<Row gutter={16}>
										<Col span={6}>
											<Statistic
												title={t('market.currentPrice')}
												value={quote?.close || 0}
												precision={2}
												valueStyle={{
													color: (quote?.change || 0) >= 0 ? '#3f8600' : '#cf1322',
												}}
												prefix={
													(quote?.change || 0) >= 0 ? (
														<RiseOutlined />
													) : (
														<FallOutlined />
													)
												}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.change')}
												value={quote?.change || 0}
												precision={2}
												valueStyle={{
													color: (quote?.change || 0) >= 0 ? '#3f8600' : '#cf1322',
												}}
												suffix={`(${quote?.change_percent?.toFixed(2) || 0}%)`}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.open')}
												value={quote?.open || 0}
												precision={2}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.prevClose')}
												value={quote?.prev_close || 0}
												precision={2}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.high')}
												value={quote?.high || 0}
												precision={2}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.low')}
												value={quote?.low || 0}
												precision={2}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.volume')}
												value={quote?.volume || 0}
											/>
										</Col>
										<Col span={6}>
											<Statistic
												title={t('market.updateTime')}
												value={
													quote?.timestamp
														? dayjs(quote.timestamp).format('HH:mm:ss')
														: '-'
												}
											/>
										</Col>
									</Row>
								</Spin>
							</Card>
						</Col>

						{/* K线图 */}
						<Col span={24}>
							<Card
								title={t('market.klineChart')}
								extra={
									<RangePicker
										value={dateRange}
										onChange={handleDateRangeChange}
										format="YYYY-MM-DD"
									/>
								}
							>
								<Spin spinning={loadingHistory}>
									{history.length > 0 ? (
										<ReactECharts option={getChartOption()} style={{ height: 400 }} />
									) : (
										<div style={{ textAlign: 'center', padding: 40 }}>
											{t('market.noData')}
										</div>
									)}
								</Spin>
							</Card>
						</Col>
					</>
				)}
			</Row>
		</div>
	);
}
