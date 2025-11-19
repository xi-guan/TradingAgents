# TradingAgents Backend

TradingAgents Web 后端服务，基于 FastAPI 构建。

## 技术栈

- **框架**: FastAPI 0.115+
- **数据库**: TimescaleDB (PostgreSQL 16+)
- **缓存**: Redis 7.4+
- **向量数据库**: Qdrant 1.12+
- **任务队列**: Celery
- **ORM**: SQLAlchemy 2.0+

## 项目结构

```
backend/
├── app/
│   ├── api/v1/              # API 路由
│   ├── core/                # 核心模块（数据库、Redis、WebSocket）
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic Schemas
│   ├── services/            # 业务逻辑
│   ├── tasks/               # Celery 异步任务
│   ├── middleware/          # 中间件
│   ├── utils/               # 工具函数
│   ├── locales/             # 国际化资源
│   ├── config.py            # 配置管理
│   └── main.py              # 应用入口
├── alembic/                 # 数据库迁移
├── tests/                   # 测试
├── pyproject.toml           # 项目配置
└── .env.example             # 环境变量示例
```

## 快速开始

### 1. 环境准备

```bash
# 复制环境变量
cp .env.example .env

# 编辑 .env 填入实际配置
vim .env
```

### 2. 安装依赖

```bash
# 使用 pip
cd backend
pip install -e .

# 或使用 uv（推荐）
uv sync
```

### 3. 启动数据库（Docker）

```bash
# 启动 TimescaleDB, Redis, Qdrant
docker-compose up -d timescaledb redis qdrant
```

### 4. 运行数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 推荐方式：使用 uv
uv run python -m app.server

# 或者直接使用 Python
python -m app.server

# 或者使用 uvicorn（不推荐）
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

访问：
- API 文档: http://localhost:8005/api/docs
- ReDoc: http://localhost:8005/api/redoc

## 核心功能

### 1. 用户认证
- JWT Token 认证
- 用户注册/登录
- 权限管理

### 2. 市场数据
- 支持 A股、港股、美股
- 实时行情（Redis 缓存）
- 历史数据（TimescaleDB）
- 多数据源支持（Tushare, AkShare, yfinance）

### 3. 智能分析
- 集成 TradingAgents 多智能体框架
- Celery 异步任务处理
- WebSocket 实时进度推送
- 分析结果存储

### 4. 模拟交易
- 多货币账户（CNY, HKD, USD）
- 订单管理
- 持仓管理
- 交易历史

### 5. 国际化
- 中英文双语支持
- 动态语言切换

## API 端点

### 认证
```
POST   /api/v1/auth/register      # 用户注册
POST   /api/v1/auth/login         # 用户登录
POST   /api/v1/auth/refresh       # 刷新 Token
```

### 股票数据
```
GET    /api/v1/stocks/search      # 搜索股票
GET    /api/v1/stocks/{symbol}    # 获取股票详情
```

### 分析任务
```
POST   /api/v1/analysis/start     # 启动分析
GET    /api/v1/analysis/{id}      # 获取分析结果
```

### 模拟交易
```
GET    /api/v1/trading/account    # 获取账户
POST   /api/v1/trading/orders     # 创建订单
```

### WebSocket
```
WS     /api/v1/ws/{user_id}       # WebSocket 连接
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/api/v1/` 创建新的路由文件
2. 定义 Pydantic Schema (`app/schemas/`)
3. 实现业务逻辑 (`app/services/`)
4. 在 `app/api/v1/__init__.py` 注册路由

### 添加数据库模型

1. 在 `app/models/` 创建模型
2. 生成迁移: `alembic revision --autogenerate -m "描述"`
3. 执行迁移: `alembic upgrade head`

### 添加 Celery 任务

1. 在 `app/tasks/` 创建任务文件
2. 使用 `@celery_app.task` 装饰器
3. 启动 worker: `celery -A app.tasks.celery_app worker`

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接 URL | - |
| REDIS_URL | Redis 连接 URL | redis://localhost:6379/0 |
| QDRANT_URL | Qdrant 连接 URL | http://localhost:6333 |
| OPENAI_API_KEY | OpenAI API Key | - |
| TUSHARE_TOKEN | Tushare Token | - |
| SECRET_KEY | 应用密钥 | - |
| JWT_SECRET_KEY | JWT 密钥 | - |

## 测试

```bash
# 运行测试
pytest

# 测试覆盖率
pytest --cov=app
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker-compose build backend

# 启动服务
docker-compose up -d
```

### 生产环境配置

1. 设置环境变量
2. 关闭 DEBUG 模式
3. 配置 CORS 允许的域名
4. 使用强密钥
5. 配置日志级别

## 许可证

MIT
