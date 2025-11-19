# TradingAgents Frontend

TradingAgents Web 前端应用，基于 React + Vite 构建。

## 技术栈

- **框架**: React 18.3+
- **构建工具**: Vite 6.0+
- **语言**: TypeScript 5.7+
- **状态管理**: Zustand 5.0+
- **路由**: React Router 7.1+
- **UI 组件**: Ant Design 5.22+
- **图表**: ECharts 5.5+
- **国际化**: react-i18next 15.1+
- **HTTP 客户端**: Axios 1.7+
- **WebSocket**: Socket.IO Client 4.8+
- **包管理**: pnpm 9.0+
- **代码质量**: Biome 1.9+

## 项目结构

```
frontend/
├── public/
│   └── locales/              # 国际化资源
│       ├── zh-CN/
│       │   └── translation.json
│       └── en-US/
│           └── translation.json
├── src/
│   ├── components/           # 公共组件
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── MainLayout.tsx
│   ├── pages/                # 页面组件
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   └── Analysis/
│   ├── stores/               # Zustand 状态管理
│   │   ├── authStore.ts
│   │   ├── analysisStore.ts
│   │   └── uiStore.ts
│   ├── services/             # API 服务
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   ├── stockService.ts
│   │   ├── analysisService.ts
│   │   └── websocket.ts
│   ├── types/                # TypeScript 类型定义
│   ├── utils/                # 工具函数
│   ├── styles/               # 全局样式
│   ├── App.tsx               # 应用主组件
│   └── main.tsx              # 应用入口
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── biome.json
```

## 快速开始

### 1. 安装依赖

```bash
# 使用 pnpm（推荐）
pnpm install

# 或使用 npm
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env
vim .env
```

### 3. 启动开发服务器

```bash
pnpm dev
```

访问 http://localhost:3000

### 4. 构建生产版本

```bash
pnpm build
```

构建产物在 `dist/` 目录。

### 5. 预览生产构建

```bash
pnpm preview
```

## 开发指南

### 代码规范

项目使用 Biome 进行代码检查和格式化：

```bash
# 检查代码
pnpm lint

# 自动修复
pnpm lint:fix

# 格式化代码
pnpm format
```

### 类型检查

```bash
pnpm type-check
```

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 添加路由
3. 在 `src/components/Layout/Sidebar.tsx` 添加菜单项
4. 在翻译文件添加对应的文本

### 添加新的 API 服务

1. 在 `src/types/` 定义类型
2. 在 `src/services/` 创建服务文件
3. 在对应的 store 中调用服务

### 状态管理

使用 Zustand 管理全局状态：

```typescript
// 在组件中使用
import { useAuthStore } from '@/stores'

function MyComponent() {
  const { user, login, logout } = useAuthStore()
  // ...
}
```

### 国际化

支持中英文切换：

```typescript
// 在组件中使用
import { useTranslation } from 'react-i18next'

function MyComponent() {
  const { t } = useTranslation()
  return <div>{t('common.login')}</div>
}
```

翻译文件位于：
- `public/locales/zh-CN/translation.json`
- `public/locales/en-US/translation.json`

## 核心功能

### 1. 用户认证
- JWT Token 认证
- 自动刷新 Token
- 受保护的路由

### 2. 股票分析
- 搜索股票
- 配置分析参数
- 实时进度显示
- 查看分析结果

### 3. 市场数据
- 实时行情
- 历史数据
- K线图表

### 4. WebSocket 实时推送
- 分析进度更新
- 实时行情推送
- 交易更新通知

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | 后端 API 地址 | http://localhost:8000 |
| VITE_WS_URL | WebSocket 地址 | ws://localhost:8000 |

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -f ../docker/frontend.Dockerfile -t tradingagents-frontend .

# 运行容器
docker run -p 80:80 tradingagents-frontend
```

### Nginx 部署

1. 构建生产版本：`pnpm build`
2. 将 `dist/` 目录部署到 Nginx
3. 配置 Nginx 反向代理到后端 API

示例 Nginx 配置：

```nginx
server {
    listen 80;
    server_name example.com;

    root /usr/share/nginx/html;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /socket.io {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 故障排除

### 开发服务器启动失败

1. 检查端口 3000 是否被占用
2. 清除 node_modules 重新安装：`rm -rf node_modules && pnpm install`

### API 请求失败

1. 检查后端服务是否启动
2. 检查 `.env` 中的 API 地址配置
3. 查看浏览器控制台的网络请求

### 样式问题

1. 清除浏览器缓存
2. 检查 Ant Design 的主题配置

## 许可证

MIT
