# TradingAgents Web UI - 开发文档

> 本文档整合了项目开发过程中的所有重要信息，包括实现状态、功能对比、技术细节等。

## 📋 目录

- [项目概览](#项目概览)
- [快速开始](#快速开始)
- [实现状态](#实现状态)
- [功能对比分析](#功能对比分析)
- [最新实现 (Priority 5 & 6)](#最新实现-priority-5--6)
- [技术架构](#技术架构)
- [下一步计划](#下一步计划)

---

## 项目概览

为现有的 TradingAgents 终端应用添加现代化的 Web UI，支持中文和中国股市（A股、港股）。

### 核心目标

1. ✅ **Web 化**: 从终端应用转变为现代 Web 应用
2. ✅ **国际化**: 完整的中英文支持
3. ✅ **中国市场**: 支持 A股、港股、美股
4. ✅ **实时交互**: WebSocket 实时数据推送
5. ✅ **现代架构**: FastAPI + React + TimescaleDB

### 技术栈

**后端 (Backend)**:
- FastAPI 0.115+ (异步 Web 框架)
- SQLAlchemy 2.0 (异步 ORM)
- TimescaleDB (时序数据库)
- Redis 7.4 (缓存和消息队列)
- Qdrant (向量数据库)
- Alembic (数据库迁移)

**前端 (Frontend)**:
- React 19.0 (最新版本)
- TypeScript 5.7
- Ant Design 5.22 (UI 组件库)
- Zustand 5.0 (状态管理)
- React Router 7.1 (路由)
- Vite 6.0 (构建工具)
- i18next (国际化)

**数据源**:
- Tushare (A股数据 - 付费)
- AkShare (A股数据 - 免费)
- YFinance (国际股市)
- Alpha Vantage (新闻和情绪分析)

---

## 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone <repository-url>
cd TradingAgents

# 安装 uv (如果还没有)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 配置环境变量

```bash
# 后端配置
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入必要的 API keys

# 前端配置
cp frontend/.env.example frontend/.env
```

### 3. 启动服务

#### 3.1 启动 Docker 服务（数据库）

```bash
docker compose up -d
```

这会启动：
- TimescaleDB (端口 5437)
- Redis (端口 6385)
- Qdrant (端口 6435, 6436)

#### 3.2 初始化数据库

```bash
cd backend
alembic upgrade head
```

#### 3.3 启动后端

```bash
cd backend
uv run python -m app.server
```

后端将在 http://localhost:8005 启动
- API 文档: http://localhost:8005/api/docs
- ReDoc: http://localhost:8005/api/redoc

#### 3.4 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

前端将在 http://localhost:3005 启动

---

## 实现状态

### ✅ 已完成 (100%)

#### 1. 架构设计
- ✅ 完整的架构设计文档 (`docs/web-ui-architecture.md`)
- ✅ 技术栈选型和系统架构
- ✅ 数据库 Schema 设计
- ✅ API 接口设计

#### 2. 后端基础框架
- ✅ FastAPI 应用架构
- ✅ 数据库连接管理（SQLAlchemy + AsyncPG）
- ✅ Redis 客户端和缓存
- ✅ WebSocket 连接管理器
- ✅ 错误处理和日志中间件
- ✅ 市场工具函数（代码标准化、涨跌停检测）
- ✅ 交易时间判断（A股、港股、美股）
- ✅ 国际化支持（中英文）

#### 3. 前端应用
- ✅ React 19 + TypeScript + Vite 项目
- ✅ Ant Design UI 组件库
- ✅ Zustand 状态管理
- ✅ React Router 路由
- ✅ i18next 国际化
- ✅ 登录页面
- ✅ Dashboard 页面
- ✅ 分析页面
- ✅ 布局组件（Header, Sidebar）

#### 4. Docker 部署
- ✅ Docker Compose 配置（Mac ARM 支持）
- ✅ TimescaleDB + Redis + Qdrant 容器
- ✅ 端口配置（避免冲突）

#### 5. 核心功能 API

##### Priority 1: 交易 API ✅
- `/api/v1/trading/accounts` - 账户管理
- `/api/v1/trading/orders` - 订单管理
- `/api/v1/trading/positions` - 持仓管理

##### Priority 2: 技术指标库 ✅
- `/api/v1/indicators/calculate` - 计算技术指标
- 支持 20+ 常用指标（MA, EMA, MACD, RSI, KDJ 等）

##### Priority 3: 收藏夹/监控清单 ✅
- `/api/v1/watchlist` - 监控清单 CRUD
- `/api/v1/watchlist/{id}/stocks` - 股票管理

##### Priority 4: 批量分析 ✅
- `/api/v1/batch-analysis/tasks` - 批量分析任务
- `/api/v1/batch-analysis/tasks/{id}` - 任务状态和结果

##### Priority 5: 新闻和财务数据 ✅
- `/api/v1/news/{symbol}` - 股票新闻（Alpha Vantage）
- `/api/v1/financials/{symbol}/statements` - 财务报表（YFinance）
- `/api/v1/financials/{symbol}/metrics` - 财务指标

##### Priority 6: 股票筛选器 ✅
- `/api/v1/screener/screen` - 股票筛选
- `/api/v1/screener/fields` - 可用筛选字段
- 支持 12 个字段，8 种运算符

### 🔧 最近修复

#### 代码审查修复 (2025-11-19)
- ✅ 修复 news_service.py 导入路径错误
- ✅ 修复 Stock/StockQuote 模型与数据库架构不匹配
- ✅ 修复筛选服务 JOIN 逻辑
- ✅ 添加 market_cap 字段和迁移
- ✅ 为所有新端点添加身份验证
- ✅ 为所有 API 端点添加错误处理

#### 配置更新 (2025-11-19)
- ✅ 重组文档目录结构
- ✅ 更新 Docker Compose（Mac ARM 支持）
- ✅ 更新端口配置（避免冲突）
- ✅ 标准化服务器启动方式（`python -m app.server`）

---

## 功能对比分析

### 与 TradingAgents-CN 的对比

> 基于 2025-11-19 的对比分析

#### 整体完成度

| 类别 | 完成度 | 说明 |
|------|--------|------|
| ✅ 已完成 | 42 功能 (33%) | 核心功能已实现 |
| 🟡 部分完成 | 35 功能 (27%) | 基础框架完成，待细化 |
| ❌ 缺失 | 48 功能 (37%) | 待开发 |
| ➕ 独有功能 | 5 功能 (4%) | 我们的优势 |

**总体完成度**: ~60%

#### 我们的优势 ➕

1. **React 19**: 使用最新版本，支持 Compiler 和 Actions
2. **TimescaleDB**: 专为时序数据优化
3. **更清晰的架构**: FastAPI + React 分离，易维护
4. **类型安全**: 全面使用 TypeScript 和 Pydantic
5. **容器化**: 完整的 Docker 支持

#### 主要差距 ❌

**缺失的重要功能**:
1. 高级股票筛选（行业、财务比率筛选）
2. 消息通知系统
3. 定时任务/调度系统
4. 多数据源同步和降级
5. 使用统计和限流

**待完善的功能** 🟡:
1. 交易执行引擎（基础框架已有）
2. 风险管理系统
3. 回测系统
4. 报告生成
5. 数据导出

### 详细功能对比表

#### 核心交易功能

| 功能 | TradingAgents-CN | 当前状态 | 说明 |
|------|------------------|----------|------|
| 模拟账户管理 | ✅ | ✅ | API 已实现 |
| 订单管理 | ✅ | ✅ | CRUD + 状态管理 |
| 持仓管理 | ✅ | ✅ | 实时计算盈亏 |
| 订单执行引擎 | ✅ | 🟡 | 基础框架 |
| 风险管理 | ✅ | ❌ | 待实现 |
| 交易历史 | ✅ | 🟡 | 基础查询 |

#### 数据分析

| 功能 | TradingAgents-CN | 当前状态 | 说明 |
|------|------------------|----------|------|
| 技术指标计算 | ✅ | ✅ | 20+ 指标 |
| 批量分析 | ✅ | ✅ | 异步任务 |
| 财务数据 | ✅ | ✅ | YFinance 集成 |
| 新闻数据 | ✅ | ✅ | Alpha Vantage |
| 股票筛选 | ✅ | ✅ | 12 字段，8 运算符 |
| 回测系统 | ✅ | ❌ | 待实现 |

#### 用户界面

| 功能 | TradingAgents-CN | 当前状态 | 说明 |
|------|------------------|----------|------|
| Web UI | ✅ (Streamlit) | ✅ (React) | 更现代化 |
| 图表展示 | ✅ | 🟡 | 待集成 ECharts |
| 实时更新 | ✅ | ✅ | WebSocket |
| 移动端适配 | ❌ | ❌ | 都未实现 |
| 主题切换 | ✅ | 🟡 | Ant Design 支持 |

---

## 最新实现 (Priority 5 & 6)

### Priority 5: 新闻和财务数据集成

#### 实现概览

**目标**: 为股票分析提供新闻情绪和财务数据支持

**数据源**:
- Alpha Vantage API (新闻 + 情绪分析)
- YFinance (财务报表 + 指标)

#### 数据库 Schema

**1. news_articles 表**
```sql
CREATE TABLE news_articles (
  id UUID PRIMARY KEY,
  symbol VARCHAR(20),
  market VARCHAR(10),
  title VARCHAR(500),
  summary TEXT,
  url VARCHAR(1000),
  source VARCHAR(100),
  sentiment VARCHAR(20),        -- positive/negative/neutral
  sentiment_score FLOAT,        -- -1.0 to 1.0
  published_at TIMESTAMP,
  created_at TIMESTAMP
);
```

**2. financial_statements 表**
```sql
CREATE TABLE financial_statements (
  id UUID PRIMARY KEY,
  symbol VARCHAR(20),
  market VARCHAR(10),
  statement_type VARCHAR(20),   -- income/balance/cashflow
  period_type VARCHAR(20),      -- annual/quarterly
  report_date DATE,
  -- 利润表字段
  revenue NUMERIC(20, 2),
  net_income NUMERIC(20, 2),
  -- 资产负债表字段
  total_assets NUMERIC(20, 2),
  total_liabilities NUMERIC(20, 2),
  -- 现金流量表字段
  operating_cashflow NUMERIC(20, 2),
  ...
);
```

**3. financial_metrics 表**
```sql
CREATE TABLE financial_metrics (
  id UUID PRIMARY KEY,
  symbol VARCHAR(20),
  market VARCHAR(10),
  report_date DATE,
  -- 估值指标
  pe_ratio NUMERIC(10, 2),
  pb_ratio NUMERIC(10, 2),
  -- 盈利能力
  roe NUMERIC(10, 4),
  roa NUMERIC(10, 4),
  gross_margin NUMERIC(10, 4),
  net_margin NUMERIC(10, 4),
  -- 偿债能力
  debt_to_equity NUMERIC(10, 4),
  current_ratio NUMERIC(10, 4),
  ...
);
```

#### API 端点

**新闻 API**:
```
GET  /api/v1/news/{symbol}
  - Query: market (CN|HK|US), limit, hours
  - Returns: 新闻列表（按时间倒序）

POST /api/v1/news/{symbol}/refresh
  - 强制从 API 获取最新新闻
```

**财务数据 API**:
```
GET  /api/v1/financials/{symbol}/statements
  - Query: market, statement_type, period_type, limit
  - Returns: 财务报表列表

GET  /api/v1/financials/{symbol}/metrics
  - Query: market, limit
  - Returns: 财务指标列表

POST /api/v1/financials/{symbol}/statements/refresh
  - 强制从 API 刷新财务数据
```

#### 使用示例

```python
# 获取股票新闻
GET /api/v1/news/AAPL?market=US&limit=10

# 获取最近24小时的新闻
GET /api/v1/news/000001?market=CN&hours=24

# 获取财务报表
GET /api/v1/financials/AAPL/statements?market=US&statement_type=income

# 获取财务指标
GET /api/v1/financials/AAPL/metrics?market=US&limit=5
```

---

### Priority 6: 股票筛选系统

#### 实现概览

**目标**: 提供灵活的股票筛选功能，支持多种条件组合

**特性**:
- 支持 12 个筛选字段
- 支持 8 种运算符
- 支持多条件 AND 组合
- 支持排序和分页

#### 支持的筛选字段

1. **价格相关**
   - `current_price` - 当前价格
   - `change_percent` - 涨跌幅
   - `volume` - 成交量

2. **市值和估值**
   - `market_cap` - 市值
   - `pe_ratio` - 市盈率
   - `pb_ratio` - 市净率

3. **盈利能力**
   - `roe` - 净资产收益率
   - `roa` - 总资产收益率
   - `gross_margin` - 毛利率
   - `net_margin` - 净利率

4. **增长和偿债**
   - `revenue_growth` - 营收增长率
   - `debt_to_equity` - 资产负债率

#### 支持的运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| `gt` | 大于 | pe_ratio > 15 |
| `gte` | 大于等于 | roe >= 0.15 |
| `lt` | 小于 | pb_ratio < 3 |
| `lte` | 小于等于 | debt_to_equity <= 0.5 |
| `eq` | 等于 | market = "CN" |
| `ne` | 不等于 | volume != 0 |
| `between` | 区间 | pe_ratio BETWEEN [10, 20] |
| `in` | 包含于 | symbol IN ["AAPL", "MSFT"] |

#### API 端点

```
POST /api/v1/screener/screen
  - Body: ScreenerRequest
  - Returns: ScreenerResponse

GET  /api/v1/screener/fields
  - Returns: 可用字段、运算符、市场列表
```

#### 使用示例

**筛选高 ROE、低 P/E 的股票**:
```json
POST /api/v1/screener/screen
{
  "market": "CN",
  "conditions": [
    {
      "field": "pe_ratio",
      "operator": "between",
      "value": [10, 20]
    },
    {
      "field": "roe",
      "operator": "gte",
      "value": 0.15
    },
    {
      "field": "debt_to_equity",
      "operator": "lte",
      "value": 0.5
    }
  ],
  "order_by": "roe",
  "order_direction": "desc",
  "limit": 50
}
```

**响应**:
```json
{
  "total": 15,
  "conditions": [...],
  "results": [
    {
      "symbol": "000001",
      "name": "平安银行",
      "market": "CN",
      "current_price": 12.50,
      "change_percent": 2.5,
      "volume": 1000000,
      "market_cap": 50000000000,
      "pe_ratio": 15.5,
      "pb_ratio": 1.2,
      "roe": 0.18,
      ...
    }
  ]
}
```

#### 实现细节

**动态查询构建**:
```python
# 使用 SQLAlchemy 动态构建查询
query = (
    select(Stock, StockQuote, FinancialMetrics)
    .outerjoin(latest_quote_subq, ...)
    .outerjoin(StockQuote, ...)
    .outerjoin(latest_metrics_subq, ...)
    .outerjoin(FinancialMetrics, ...)
)

# 应用筛选条件
for condition in conditions:
    field_obj = FIELD_MAPPING[condition.field]
    filter_expr = apply_operator(field_obj, condition.operator, condition.value)
    query = query.where(filter_expr)
```

---

## 技术架构

详细的技术架构文档请参考: [`docs/web-ui-architecture.md`](./web-ui-architecture.md)

### 系统架构图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│   Nginx     │────▶│   FastAPI   │
│  (React 19) │     │  (Reverse   │     │   Backend   │
└─────────────┘     │   Proxy)    │     └─────────────┘
                    └─────────────┘            │
                                              │
                    ┌──────────────────────────┼────────────────────┐
                    │                          │                    │
                    ▼                          ▼                    ▼
            ┌─────────────┐          ┌─────────────┐      ┌─────────────┐
            │ TimescaleDB │          │    Redis    │      │   Qdrant    │
            │  (时序数据)  │          │  (缓存/队列) │      │  (向量搜索)  │
            └─────────────┘          └─────────────┘      └─────────────┘
```

### 数据流

1. **实时行情**: Redis 缓存 → TimescaleDB 持久化
2. **历史数据**: TimescaleDB 超表存储
3. **分析任务**: Celery 异步队列
4. **WebSocket**: Redis Pub/Sub → 客户端
5. **向量搜索**: Qdrant (未来功能)

### 安全性

- ✅ JWT Token 认证
- ✅ HTTPS/WSS 加密
- ✅ CORS 配置
- ✅ SQL 注入防护（ORM）
- ✅ XSS 防护（React 自动转义）
- ⏳ 速率限制（待完善）
- ⏳ 权限管理（待完善）

---

## 下一步计划

### 短期 (1-2 周)

1. **完善现有功能**
   - [ ] 添加更多技术指标
   - [ ] 完善财务数据计算
   - [ ] 优化股票筛选性能

2. **前端开发**
   - [ ] 实现图表展示（ECharts 集成）
   - [ ] 完善交易页面
   - [ ] 添加设置页面

3. **测试和文档**
   - [ ] 编写单元测试
   - [ ] API 文档完善
   - [ ] 用户使用文档

### 中期 (2-4 周)

1. **高级功能**
   - [ ] 回测系统
   - [ ] 报告生成
   - [ ] 定时任务调度
   - [ ] 消息通知系统

2. **性能优化**
   - [ ] 数据库查询优化
   - [ ] Redis 缓存策略
   - [ ] 前端代码分割

3. **多数据源**
   - [ ] Tushare 集成
   - [ ] AkShare 集成
   - [ ] 数据源降级策略

### 长期 (1-2 月)

1. **企业级特性**
   - [ ] 用户权限系统
   - [ ] 审计日志
   - [ ] 多租户支持

2. **AI 增强**
   - [ ] Qdrant 向量搜索
   - [ ] 智能选股助手
   - [ ] 策略推荐

3. **生产部署**
   - [ ] K8s 部署配置
   - [ ] 监控和告警
   - [ ] 备份和恢复

---

## 参考资源

### 文档

- [Web UI 架构文档](./web-ui-architecture.md) - 完整的技术架构设计
- [后端 README](../backend/README.md) - 后端开发指南
- [前端 README](../frontend/README.md) - 前端开发指南

### API 文档

- Swagger UI: http://localhost:8005/api/docs
- ReDoc: http://localhost:8005/api/redoc

### 外部资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 19 文档](https://react.dev/)
- [Ant Design 文档](https://ant.design/)
- [TimescaleDB 文档](https://docs.timescale.com/)

---

## 贡献

欢迎贡献！请查看主 README 了解如何参与开发。

## 许可证

[LICENSE](../LICENSE)

---

最后更新: 2025-11-19
