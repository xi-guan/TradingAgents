# TradingAgents Web UI 架构设计方案

## 概述

本文档描述了为 TradingAgents 项目添加 Web UI、中文支持和中国股市支持的完整架构方案。

## 目标

1. ✅ 保留现有的 CLI 和核心 LangGraph 交易逻辑
2. ✅ 添加现代化的 Web UI 界面
3. ✅ 完整的中文/英文双语支持
4. ✅ 支持中国 A股、港股（保留现有美股支持）
5. ✅ 实时数据推送和进度追踪
6. ✅ 用户认证和多用户管理
7. ✅ 模拟交易和回测功能

## 技术栈

### 后端技术
| 组件 | 技术选择 | 版本 | 用途 |
|------|---------|------|------|
| API 框架 | FastAPI | 0.115+ | RESTful API + WebSocket |
| ASGI 服务器 | Uvicorn | 0.32+ | 异步应用服务器 |
| 时序数据库 | TimescaleDB | 2.17+ | 存储股票历史数据 |
| 关系数据库 | PostgreSQL | 16+ | 用户数据、配置 |
| 缓存层 | Redis | 7.4+ | 实时数据缓存、任务队列 |
| 向量数据库 | Qdrant | 1.12+ | 新闻/报告语义搜索 |
| ORM | SQLAlchemy | 2.0+ | 数据库 ORM |
| 任务队列 | Celery | 5.4+ | 异步任务处理 |
| 认证 | FastAPI-Users | 13.0+ | 用户认证和授权 |

### 前端技术
| 组件 | 技术选择 | 版本 | 用途 |
|------|---------|------|------|
| 框架 | React | 19.0+ | UI 框架（最新版本）|
| 类型系统 | TypeScript | 5.7+ | 类型安全 |
| 状态管理 | Zustand | 5.0+ | 轻量级状态管理 |
| 包管理器 | pnpm | 9.0+ | 高效包管理 |
| 代码质量 | Biome | 1.9+ | Linter + Formatter |
| 构建工具 | Vite | 6.0+ | 快速构建工具 |
| UI 组件库 | Ant Design | 5.22+ | React 组件库（支持中文）|
| 图表库 | Apache ECharts | 5.5+ | 数据可视化 |
| 路由 | React Router | 7.1+ | 前端路由 |
| HTTP 客户端 | Axios | 1.7+ | API 调用 |
| WebSocket | Socket.IO Client | 4.8+ | 实时通信 |
| 国际化 | react-i18next | 15.1+ | 多语言支持 |
| 日期处理 | Day.js | 1.11+ | 轻量级日期库 |
| 表单 | React Hook Form | 7.54+ | 表单管理 |
| 不可变数据 | Immer | 10.1+ | 不可变状态更新 |

### 核心保留技术（现有项目）
| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 智能体框架 | LangGraph | 0.4+ | 多智能体编排 |
| LLM 集成 | LangChain | 最新 | LLM 工具链 |
| 数据处理 | Pandas | 2.3+ | 数据分析 |
| 中国数据源 | Tushare, AkShare | 最新 | A股数据 |
| 美股数据源 | yfinance | 0.2+ | 美股数据 |

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React App (Vite + TypeScript)                           │  │
│  │  - Zustand State Management                              │  │
│  │  - Ant Design Components                                 │  │
│  │  - ECharts Visualization                                 │  │
│  │  - react-i18next (中文/English)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↕ REST API + WebSocket                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Backend Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application                                     │  │
│  │  - RESTful API Endpoints                                 │  │
│  │  - WebSocket Manager (实时推送)                          │  │
│  │  - Authentication & Authorization                        │  │
│  │  - Rate Limiting & Caching                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Business Logic Layer                                    │  │
│  │  - TradingAgents Integration (LangGraph)                 │  │
│  │  - Market Data Service                                   │  │
│  │  - Analysis Service                                      │  │
│  │  - Trading Simulation Service                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Celery Workers (异步任务)                               │  │
│  │  - Stock Analysis Tasks                                  │  │
│  │  - Data Sync Tasks                                       │  │
│  │  - Report Generation                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Data Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ TimescaleDB │  │    Redis    │  │   Qdrant    │            │
│  │ (时序数据)  │  │  (缓存/队列)│  │ (向量搜索)  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL (用户、配置、交易记录)                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      External Services                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Tushare API │  │ AkShare API │  │ OpenAI API  │            │
│  │   (A股)     │  │   (A股)     │  │   (LLM)     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐                              │
│  │ yfinance    │  │Alpha Vantage│                              │
│  │  (美股)     │  │  (美股)     │                              │
│  └─────────────┘  └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

## 项目目录结构

```
TradingAgents/
├── backend/                              # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI 应用入口
│   │   ├── config.py                    # 配置管理
│   │   ├── dependencies.py              # 依赖注入
│   │   │
│   │   ├── api/                         # API 路由
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py             # 认证接口
│   │   │   │   ├── users.py            # 用户管理
│   │   │   │   ├── analysis.py         # 分析任务接口
│   │   │   │   ├── stocks.py           # 股票数据接口
│   │   │   │   ├── market_data.py      # 市场数据接口
│   │   │   │   ├── trading.py          # 模拟交易接口
│   │   │   │   ├── portfolio.py        # 投资组合接口
│   │   │   │   ├── websocket.py        # WebSocket 接口
│   │   │   │   └── reports.py          # 报告接口
│   │   │   └── __init__.py
│   │   │
│   │   ├── core/                        # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── database.py             # 数据库连接
│   │   │   ├── redis_client.py         # Redis 客户端
│   │   │   ├── qdrant_client.py        # Qdrant 客户端
│   │   │   ├── security.py             # 安全相关
│   │   │   └── websocket_manager.py    # WebSocket 管理器
│   │   │
│   │   ├── models/                      # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py                 # 用户模型
│   │   │   ├── stock.py                # 股票模型
│   │   │   ├── analysis.py             # 分析任务模型
│   │   │   ├── trading.py              # 交易模型
│   │   │   └── portfolio.py            # 投资组合模型
│   │   │
│   │   ├── schemas/                     # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── stock.py
│   │   │   ├── analysis.py
│   │   │   ├── trading.py
│   │   │   └── common.py
│   │   │
│   │   ├── services/                    # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py     # 分析服务
│   │   │   ├── market_data_service.py  # 市场数据服务
│   │   │   ├── trading_service.py      # 交易服务
│   │   │   ├── user_service.py         # 用户服务
│   │   │   └── tradingagents_service.py # TradingAgents 集成
│   │   │
│   │   ├── tasks/                       # Celery 任务
│   │   │   ├── __init__.py
│   │   │   ├── analysis_tasks.py       # 分析任务
│   │   │   ├── data_sync_tasks.py      # 数据同步任务
│   │   │   └── report_tasks.py         # 报告生成任务
│   │   │
│   │   ├── middleware/                  # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py
│   │   │   ├── rate_limit.py
│   │   │   └── logging_middleware.py
│   │   │
│   │   ├── utils/                       # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── i18n.py                 # 国际化工具
│   │   │   ├── market_utils.py         # 市场工具
│   │   │   └── trading_time.py         # 交易时间判断
│   │   │
│   │   └── locales/                     # 国际化资源
│   │       ├── zh_CN/
│   │       │   └── messages.json
│   │       └── en_US/
│   │           └── messages.json
│   │
│   ├── alembic/                         # 数据库迁移
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                           # 测试
│   ├── pyproject.toml                   # 后端依赖
│   └── .env.example                     # 环境变量示例
│
├── frontend/                            # React 前端
│   ├── public/
│   │   └── locales/                    # 国际化资源
│   │       ├── zh-CN/
│   │       │   └── translation.json
│   │       └── en-US/
│   │           └── translation.json
│   │
│   ├── src/
│   │   ├── main.tsx                    # 应用入口
│   │   ├── App.tsx                     # 主组件
│   │   │
│   │   ├── components/                 # 公共组件
│   │   │   ├── Layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── StockCard/
│   │   │   ├── AnalysisProgress/
│   │   │   ├── TradingChart/
│   │   │   └── LanguageSwitch/
│   │   │
│   │   ├── pages/                      # 页面组件
│   │   │   ├── Login/
│   │   │   ├── Dashboard/
│   │   │   ├── Analysis/
│   │   │   ├── MarketData/
│   │   │   ├── Trading/
│   │   │   ├── Portfolio/
│   │   │   └── Reports/
│   │   │
│   │   ├── stores/                     # Zustand Stores
│   │   │   ├── authStore.ts
│   │   │   ├── analysisStore.ts
│   │   │   ├── marketStore.ts
│   │   │   ├── tradingStore.ts
│   │   │   └── uiStore.ts
│   │   │
│   │   ├── services/                   # API 服务
│   │   │   ├── api.ts                 # Axios 配置
│   │   │   ├── authService.ts
│   │   │   ├── analysisService.ts
│   │   │   ├── stockService.ts
│   │   │   ├── tradingService.ts
│   │   │   └── websocket.ts
│   │   │
│   │   ├── hooks/                      # 自定义 Hooks
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useRealTimeData.ts
│   │   │   └── useAnalysisProgress.ts
│   │   │
│   │   ├── utils/                      # 工具函数
│   │   │   ├── i18n.ts                # i18next 配置
│   │   │   ├── format.ts
│   │   │   └── market.ts
│   │   │
│   │   ├── types/                      # TypeScript 类型
│   │   │   ├── stock.ts
│   │   │   ├── analysis.ts
│   │   │   └── trading.ts
│   │   │
│   │   └── styles/                     # 样式文件
│   │       ├── global.css
│   │       └── variables.css
│   │
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── biome.json                      # Biome 配置
│   └── .env.example
│
├── tradingagents/                       # 核心交易智能体（保留现有）
│   ├── agents/
│   ├── graph/
│   ├── dataflows/
│   └── ...
│
├── cli/                                 # CLI 工具（保留现有）
│   └── ...
│
├── docker/                              # Docker 配置
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   ├── timescaledb.Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml                   # Docker Compose
├── docker-compose.dev.yml               # 开发环境
├── .env.example                         # 环境变量示例
└── README.md
```

## 核心功能模块

### 1. 用户认证与授权

**技术实现**：
- FastAPI-Users：用户注册、登录、JWT Token
- 权限控制：基于角色的访问控制（RBAC）
- 多用户隔离：每个用户独立的分析任务和交易账户

**数据模型**：
```python
# backend/app/models/user.py
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    preferred_language: str = "zh_CN"  # zh_CN, en_US
    created_at: datetime
    updated_at: datetime
```

### 2. 市场数据服务

**数据源整合**：
```python
# backend/app/services/market_data_service.py
class MarketDataService:
    """统一的市场数据服务"""

    def __init__(self):
        # 中国股市数据源
        self.tushare = TushareProvider()
        self.akshare = AkShareProvider()

        # 美股数据源
        self.yfinance = YFinanceProvider()
        self.alpha_vantage = AlphaVantageProvider()

    async def get_stock_data(
        self,
        symbol: str,
        market: Literal["CN", "HK", "US"],
        start_date: date,
        end_date: date
    ) -> StockData:
        """获取股票数据（自动选择数据源）"""
        if market == "CN":
            return await self.tushare.get_daily_data(symbol, start_date, end_date)
        elif market == "HK":
            return await self.yfinance.get_daily_data(f"{symbol}.HK", start_date, end_date)
        else:  # US
            return await self.yfinance.get_daily_data(symbol, start_date, end_date)
```

**TimescaleDB 数据存储**：
```sql
-- 股票日线数据表（使用 TimescaleDB 超表）
CREATE TABLE stock_daily_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,  -- CN, HK, US
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    amount DECIMAL(20, 4),
    PRIMARY KEY (time, symbol, market)
);

-- 转换为超表
SELECT create_hypertable('stock_daily_data', 'time');

-- 创建索引
CREATE INDEX idx_symbol_market ON stock_daily_data (symbol, market, time DESC);
```

### 3. 智能分析服务

**集成现有 TradingAgents**：
```python
# backend/app/services/tradingagents_service.py
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

class TradingAgentsService:
    """TradingAgents 分析服务包装器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or DEFAULT_CONFIG.copy()
        # 支持中国股市配置
        self.config["data_vendors"]["core_stock_apis"] = "auto"  # 自动选择
        self.config["data_vendors"]["news_data"] = "alpha_vantage"

    async def analyze_stock(
        self,
        symbol: str,
        market: str,
        analysis_date: str,
        user_id: str,
        task_id: str
    ) -> Dict:
        """执行股票分析（异步任务）"""
        # 初始化 TradingAgents
        ta = TradingAgentsGraph(debug=True, config=self.config)

        # 发送进度更新
        await self._update_progress(task_id, 0, "初始化分析...")

        # 执行分析
        _, decision = ta.propagate(symbol, analysis_date)

        # 保存结果到数据库
        await self._save_analysis_result(user_id, symbol, market, decision)

        return decision

    async def _update_progress(self, task_id: str, progress: int, message: str):
        """更新分析进度（通过 WebSocket 推送）"""
        await websocket_manager.broadcast_to_user(
            user_id,
            {
                "type": "analysis_progress",
                "task_id": task_id,
                "progress": progress,
                "message": message
            }
        )
```

### 4. 实时数据推送

**WebSocket 管理器**：
```python
# backend/app/core/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, Set

class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 用户 ID -> WebSocket 连接集合
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, user_id: str, message: dict):
        """向特定用户的所有连接广播消息"""
        if user_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)

            # 清理死连接
            self.active_connections[user_id] -= dead_connections
```

**WebSocket 路由**：
```python
# backend/app/api/v1/websocket.py
from fastapi import APIRouter, WebSocket, Depends
from app.core.websocket_manager import websocket_manager

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str  # 通过查询参数传递 JWT
):
    # 验证 token
    user = await verify_websocket_token(token)
    if not user or str(user.id) != user_id:
        await websocket.close(code=1008)
        return

    # 建立连接
    await websocket_manager.connect(websocket, user_id)

    try:
        while True:
            # 接收客户端消息（可选：支持双向通信）
            data = await websocket.receive_json()
            # 处理消息...
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id)
```

### 5. 模拟交易系统

**交易账户模型**：
```python
# backend/app/models/trading.py
class TradingAccount(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    account_type: str = "paper"  # paper, live (未来扩展)

    # 多货币账户
    cash_cny: Decimal = Field(default=Decimal("1000000"))  # 100万人民币
    cash_hkd: Decimal = Field(default=Decimal("1000000"))  # 100万港币
    cash_usd: Decimal = Field(default=Decimal("100000"))   # 10万美元

    created_at: datetime
    updated_at: datetime

class Position(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(foreign_key="tradingaccount.id")
    symbol: str
    market: str  # CN, HK, US
    quantity: int
    avg_cost: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    created_at: datetime
    updated_at: datetime

class Order(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    account_id: UUID = Field(foreign_key="tradingaccount.id")
    symbol: str
    market: str
    side: str  # buy, sell
    order_type: str  # market, limit
    quantity: int
    price: Optional[Decimal]
    status: str  # pending, filled, cancelled
    filled_at: Optional[datetime]
    created_at: datetime
```

### 6. 国际化支持

**后端 i18n**：
```python
# backend/app/utils/i18n.py
from typing import Dict
import json

class I18n:
    """国际化工具类"""

    def __init__(self):
        self.messages: Dict[str, Dict[str, str]] = {}
        self._load_messages()

    def _load_messages(self):
        # 加载中文
        with open("app/locales/zh_CN/messages.json", "r", encoding="utf-8") as f:
            self.messages["zh_CN"] = json.load(f)

        # 加载英文
        with open("app/locales/en_US/messages.json", "r", encoding="utf-8") as f:
            self.messages["en_US"] = json.load(f)

    def t(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """翻译文本"""
        message = self.messages.get(locale, {}).get(key, key)
        return message.format(**kwargs) if kwargs else message

# 全局实例
i18n = I18n()

# 使用示例
message = i18n.t("analysis.started", locale="zh_CN", symbol="000001")
# 输出: "开始分析股票 000001"
```

**前端 i18n**：
```typescript
// frontend/src/utils/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zhCN from '../public/locales/zh-CN/translation.json';
import enUS from '../public/locales/en-US/translation.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      'zh-CN': { translation: zhCN },
      'en-US': { translation: enUS },
    },
    lng: localStorage.getItem('language') || 'zh-CN',
    fallbackLng: 'en-US',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

**翻译文件示例**：
```json
// frontend/public/locales/zh-CN/translation.json
{
  "common": {
    "login": "登录",
    "logout": "退出",
    "submit": "提交",
    "cancel": "取消"
  },
  "dashboard": {
    "title": "控制台",
    "market_overview": "市场概览",
    "my_portfolio": "我的投资组合"
  },
  "analysis": {
    "start_analysis": "开始分析",
    "analysis_progress": "分析进度",
    "fundamental_analysis": "基本面分析",
    "technical_analysis": "技术面分析",
    "sentiment_analysis": "情绪分析"
  },
  "trading": {
    "buy": "买入",
    "sell": "卖出",
    "market_order": "市价单",
    "limit_order": "限价单"
  },
  "market": {
    "cn": "A股",
    "hk": "港股",
    "us": "美股"
  }
}
```

## API 设计

### RESTful API 端点

#### 认证相关
```
POST   /api/v1/auth/register          # 用户注册
POST   /api/v1/auth/login             # 用户登录
POST   /api/v1/auth/refresh           # 刷新 Token
GET    /api/v1/users/me               # 获取当前用户信息
PATCH  /api/v1/users/me               # 更新用户信息
```

#### 股票数据
```
GET    /api/v1/stocks/search          # 搜索股票
GET    /api/v1/stocks/{symbol}        # 获取股票详情
GET    /api/v1/stocks/{symbol}/quote  # 获取实时行情
GET    /api/v1/stocks/{symbol}/history # 获取历史数据
GET    /api/v1/stocks/{symbol}/financials # 获取财务数据
```

#### 分析任务
```
POST   /api/v1/analysis/start         # 启动分析任务
GET    /api/v1/analysis/{task_id}     # 获取分析任务状态
GET    /api/v1/analysis/{task_id}/result # 获取分析结果
GET    /api/v1/analysis/history       # 获取历史分析记录
DELETE /api/v1/analysis/{task_id}     # 删除分析任务
```

#### 模拟交易
```
GET    /api/v1/trading/account        # 获取交易账户
GET    /api/v1/trading/positions      # 获取持仓
POST   /api/v1/trading/orders         # 创建订单
GET    /api/v1/trading/orders         # 获取订单列表
GET    /api/v1/trading/orders/{order_id} # 获取订单详情
DELETE /api/v1/trading/orders/{order_id} # 取消订单
```

#### 投资组合
```
GET    /api/v1/portfolio/overview     # 投资组合概览
GET    /api/v1/portfolio/performance  # 绩效分析
GET    /api/v1/portfolio/risk         # 风险分析
```

### WebSocket 消息格式

#### 客户端 → 服务器
```json
{
  "type": "subscribe",
  "channels": ["analysis_progress", "market_data", "trading_updates"]
}
```

#### 服务器 → 客户端

**分析进度更新**：
```json
{
  "type": "analysis_progress",
  "task_id": "uuid-here",
  "progress": 45,
  "stage": "technical_analysis",
  "message": "正在进行技术面分析...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**实时行情更新**：
```json
{
  "type": "market_data",
  "symbol": "000001",
  "market": "CN",
  "price": 18.50,
  "change": 0.30,
  "change_percent": 1.65,
  "volume": 12345678,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**交易更新**：
```json
{
  "type": "trading_update",
  "event": "order_filled",
  "order_id": "uuid-here",
  "symbol": "000001",
  "side": "buy",
  "quantity": 1000,
  "price": 18.50,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 前端页面设计

### 1. 登录/注册页面
- 支持邮箱/用户名登录
- 记住登录状态
- 语言切换（中文/English）

### 2. 控制台（Dashboard）
- 市场概览（A股、港股、美股指数）
- 我的投资组合摘要
- 最近分析任务
- 快速操作入口

### 3. 股票分析页面
- 股票搜索（支持代码、名称、拼音）
- 分析参数配置
  - 分析深度（1-5级）
  - LLM 选择
  - 辩论轮数
- 实时进度显示（进度条 + 日志）
- 分析结果展示
  - 基本面分析
  - 技术面分析
  - 情绪分析
  - 新闻分析
  - 综合建议（买入/持有/卖出）
  - 风险评估

### 4. 市场数据页面
- 股票列表（分市场）
- 实时行情
- K线图（ECharts）
- 技术指标图表
- 财务数据表格

### 5. 模拟交易页面
- 账户信息（余额、盈亏）
- 下单面板
- 持仓列表
- 订单历史
- 成交记录

### 6. 投资组合页面
- 持仓概览
- 收益曲线
- 资产分布图
- 绩效指标（收益率、夏普比率、最大回撤）
- 风险分析

### 7. 报告页面
- 分析报告列表
- 报告详情查看
- 报告导出（PDF、Word）
- 报告分享

## 数据库设计

### PostgreSQL 表结构

#### 用户表
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    preferred_language VARCHAR(10) DEFAULT 'zh_CN',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 分析任务表
```sql
CREATE TABLE analysis_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,
    analysis_date DATE NOT NULL,
    depth INTEGER DEFAULT 3,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed
    progress INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analysis_tasks_user ON analysis_tasks(user_id, created_at DESC);
CREATE INDEX idx_analysis_tasks_status ON analysis_tasks(status, created_at DESC);
```

#### 交易账户表
```sql
CREATE TABLE trading_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    account_type VARCHAR(20) DEFAULT 'paper',
    cash_cny DECIMAL(20, 4) DEFAULT 1000000,
    cash_hkd DECIMAL(20, 4) DEFAULT 1000000,
    cash_usd DECIMAL(20, 4) DEFAULT 100000,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 持仓表
```sql
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES trading_accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    avg_cost DECIMAL(12, 4) NOT NULL,
    current_price DECIMAL(12, 4),
    unrealized_pnl DECIMAL(20, 4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, symbol, market)
);
```

#### 订单表
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES trading_accounts(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL,  -- buy, sell
    order_type VARCHAR(10) NOT NULL,  -- market, limit
    quantity INTEGER NOT NULL,
    price DECIMAL(12, 4),
    filled_quantity INTEGER DEFAULT 0,
    filled_price DECIMAL(12, 4),
    status VARCHAR(20) DEFAULT 'pending',  -- pending, filled, cancelled, rejected
    filled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orders_account ON orders(account_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status, created_at DESC);
```

### TimescaleDB 超表

#### 股票日线数据
```sql
CREATE TABLE stock_daily_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    amount DECIMAL(20, 4),
    turnover_rate DECIMAL(8, 4),
    PRIMARY KEY (time, symbol, market)
);

SELECT create_hypertable('stock_daily_data', 'time');
CREATE INDEX idx_symbol_market_time ON stock_daily_data (symbol, market, time DESC);
```

#### 实时行情数据（1分钟级别）
```sql
CREATE TABLE stock_minute_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    market VARCHAR(10) NOT NULL,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    volume BIGINT,
    PRIMARY KEY (time, symbol, market)
);

SELECT create_hypertable('stock_minute_data', 'time');
CREATE INDEX idx_minute_symbol_market ON stock_minute_data (symbol, market, time DESC);

-- 设置数据保留策略（保留 30 天）
SELECT add_retention_policy('stock_minute_data', INTERVAL '30 days');
```

### Redis 缓存策略

```python
# 缓存键命名规范
CACHE_KEYS = {
    # 实时行情（TTL: 5分钟）
    "stock_quote": "quote:{market}:{symbol}",

    # 股票基本信息（TTL: 1天）
    "stock_info": "info:{market}:{symbol}",

    # 用户会话（TTL: 7天）
    "user_session": "session:{user_id}",

    # 分析任务进度（TTL: 24小时）
    "task_progress": "task:{task_id}:progress",

    # API 速率限制（TTL: 1分钟）
    "rate_limit": "ratelimit:{user_id}:{endpoint}",
}
```

### Qdrant 向量数据库

```python
# 用于新闻和报告的语义搜索
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 创建集合
client = QdrantClient(host="localhost", port=6333)

# 新闻向量集合
client.create_collection(
    collection_name="news_embeddings",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# 分析报告向量集合
client.create_collection(
    collection_name="analysis_reports",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)
```

## 中国股市特殊支持

### 1. 交易时间处理

```python
# backend/app/utils/trading_time.py
from datetime import datetime, time as dtime
import pytz

CN_TIMEZONE = pytz.timezone('Asia/Shanghai')

def is_cn_trading_time(dt: datetime = None) -> bool:
    """判断是否在 A股交易时间"""
    if dt is None:
        dt = datetime.now(CN_TIMEZONE)

    # 周末不交易
    if dt.weekday() >= 5:
        return False

    # 交易时间段
    morning_start = dtime(9, 30)
    noon_end = dtime(11, 30)
    afternoon_start = dtime(13, 0)
    close_end = dtime(15, 0)

    t = dt.time()
    return (morning_start <= t <= noon_end) or (afternoon_start <= t <= close_end)

def get_latest_trading_day() -> date:
    """获取最近交易日"""
    today = datetime.now(CN_TIMEZONE).date()

    # 如果是周末，回退到周五
    while today.weekday() >= 5:
        today -= timedelta(days=1)

    return today
```

### 2. 股票代码标准化

```python
# backend/app/utils/market_utils.py
import re

def normalize_symbol(symbol: str) -> tuple[str, str]:
    """
    标准化股票代码

    返回: (标准代码, 市场)
    - A股: ("000001", "CN"), ("000001.SZ", "CN")
    - 港股: ("00700", "HK"), ("00700.HK", "HK")
    - 美股: ("AAPL", "US")
    """
    symbol = symbol.strip().upper()

    # A股
    if re.match(r'^\d{6}$', symbol):
        # 6位纯数字，判断交易所
        if symbol.startswith(('6', '5')):
            return f"{symbol}.SH", "CN"  # 上交所
        else:
            return f"{symbol}.SZ", "CN"  # 深交所

    if re.match(r'^\d{6}\.(SH|SZ)$', symbol):
        return symbol, "CN"

    # 港股
    if re.match(r'^\d{4,5}$', symbol):
        return f"{symbol}.HK", "HK"

    if re.match(r'^\d{4,5}\.HK$', symbol):
        return symbol, "HK"

    # 美股（字母开头）
    return symbol, "US"
```

### 3. 涨跌停检测

```python
# backend/app/utils/market_utils.py
def check_limit_status(
    symbol: str,
    current_price: float,
    prev_close: float
) -> tuple[bool, str]:
    """
    检测涨跌停状态

    返回: (是否涨跌停, 状态)
    """
    change_pct = (current_price - prev_close) / prev_close * 100

    # ST股票 5% 限制
    if symbol.startswith(('*ST', 'ST')):
        if change_pct >= 4.95:
            return True, "涨停"
        elif change_pct <= -4.95:
            return True, "跌停"

    # 普通股票 10% 限制
    else:
        if change_pct >= 9.95:
            return True, "涨停"
        elif change_pct <= -9.95:
            return True, "跌停"

    return False, "正常"
```

### 4. 数据源适配

```python
# backend/app/services/market_data_service.py
class ChinaMarketDataService:
    """中国股市数据服务"""

    async def get_stock_info(self, symbol: str) -> dict:
        """获取股票基本信息（优先使用 Tushare，fallback 到 AkShare）"""
        try:
            # 尝试 Tushare
            data = await self.tushare.get_stock_basic(symbol)
            return data
        except Exception as e:
            logger.warning(f"Tushare failed, fallback to AkShare: {e}")
            # Fallback 到 AkShare
            data = await self.akshare.get_stock_basic(symbol)
            return data

    async def get_realtime_quote(self, symbol: str) -> dict:
        """获取实时行情"""
        # 检查 Redis 缓存
        cache_key = f"quote:CN:{symbol}"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # 从 AkShare 获取（免费且实时）
        quote = await self.akshare.get_realtime_quote(symbol)

        # 缓存 5 分钟
        await redis.setex(cache_key, 300, json.dumps(quote))

        return quote
```

## 部署方案

### Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL + TimescaleDB
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: tradingagents-timescaledb
    environment:
      POSTGRES_DB: tradingagents
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescaledb_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - tradingagents-network

  # Redis
  redis:
    image: redis:7.4-alpine
    container_name: tradingagents-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - tradingagents-network

  # Qdrant
  qdrant:
    image: qdrant/qdrant:latest
    container_name: tradingagents-qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"
    networks:
      - tradingagents-network

  # Backend (FastAPI)
  backend:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    container_name: tradingagents-backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@timescaledb:5432/tradingagents
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
    volumes:
      - ./backend:/app
      - ./tradingagents:/app/tradingagents
    ports:
      - "8000:8000"
    depends_on:
      - timescaledb
      - redis
      - qdrant
    networks:
      - tradingagents-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker
  celery-worker:
    build:
      context: .
      dockerfile: docker/backend.Dockerfile
    container_name: tradingagents-celery
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${DB_PASSWORD}@timescaledb:5432/tradingagents
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
      - ./tradingagents:/app/tradingagents
    depends_on:
      - redis
      - timescaledb
    networks:
      - tradingagents-network
    command: celery -A app.tasks.celery_app worker --loglevel=info

  # Frontend (React)
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend.Dockerfile
    container_name: tradingagents-frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8005
      - VITE_WS_URL=ws://localhost:8005
    networks:
      - tradingagents-network
    command: pnpm dev --host

  # Nginx (生产环境)
  nginx:
    image: nginx:alpine
    container_name: tradingagents-nginx
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    networks:
      - tradingagents-network
    profiles:
      - production

volumes:
  timescaledb_data:
  redis_data:
  qdrant_data:

networks:
  tradingagents-network:
    driver: bridge
```

### 生产环境部署

**部署步骤**：

1. **准备环境变量**：
```bash
cp .env.example .env
# 编辑 .env 填入实际配置
```

2. **构建和启动服务**：
```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose --profile production up -d
```

3. **初始化数据库**：
```bash
# 运行迁移
docker-compose exec backend alembic upgrade head

# 创建 TimescaleDB 超表
docker-compose exec backend python -m app.scripts.init_timescaledb
```

4. **创建管理员用户**：
```bash
docker-compose exec backend python -m app.scripts.create_admin
```

## 开发计划

### 第一阶段：基础架构（2-3周）
- [ ] 搭建后端项目结构
- [ ] 配置 FastAPI + PostgreSQL + TimescaleDB
- [ ] 实现用户认证系统
- [ ] 搭建前端项目结构（React + Vite）
- [ ] 实现基础 UI 框架和路由
- [ ] Docker 容器化配置

### 第二阶段：市场数据集成（2周）
- [ ] 集成 Tushare、AkShare 数据源
- [ ] 实现数据获取服务
- [ ] TimescaleDB 数据存储
- [ ] Redis 缓存层
- [ ] 实时行情更新机制

### 第三阶段：分析服务（3周）
- [ ] 包装现有 TradingAgents 为服务
- [ ] 实现 Celery 异步任务
- [ ] WebSocket 实时进度推送
- [ ] 分析结果存储和展示
- [ ] 前端分析页面开发

### 第四阶段：模拟交易（2周）
- [ ] 交易账户系统
- [ ] 订单执行引擎
- [ ] 持仓管理
- [ ] 前端交易界面
- [ ] 交易历史和统计

### 第五阶段：国际化和优化（1-2周）
- [ ] 完整的中英文双语支持
- [ ] 报告导出功能
- [ ] 性能优化
- [ ] 单元测试
- [ ] 文档完善

### 第六阶段：高级功能（可选）
- [ ] Qdrant 语义搜索
- [ ] 回测系统
- [ ] 策略编辑器
- [ ] 社交功能
- [ ] 移动端适配

## 总结

本架构设计方案充分融合了：

1. **TradingAgents 的核心能力**：保留完整的 LangGraph 多智能体交易逻辑
2. **TradingAgents-CN 的成功经验**：借鉴其 Web UI 设计、中文支持和 A股集成
3. **用户指定的技术栈**：严格遵循 FastAPI、React、Zustand、TimescaleDB 等要求

关键优势：
- ✅ **现代化技术栈**：FastAPI + React + TypeScript
- ✅ **高性能**：TimescaleDB 时序数据 + Redis 缓存 + 异步处理
- ✅ **实时性**：WebSocket 推送 + 实时行情更新
- ✅ **多市场**：A股 + 港股 + 美股全覆盖
- ✅ **国际化**：完整的中英文双语支持
- ✅ **可扩展**：模块化设计，易于添加新功能
- ✅ **Docker 部署**：一键启动，环境一致

该方案为 TradingAgents 项目提供了从 CLI 到企业级 Web 应用的完整升级路径。
