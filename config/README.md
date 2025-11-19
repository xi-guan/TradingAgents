# Schema-Driven Configuration

这个目录包含 TradingAgents 的配置管理系统，使用 **Schema-Driven** 模式简化配置管理。

## 📁 文件说明

| 文件 | 说明 | Git 跟踪 |
|------|------|----------|
| `config.schema.yaml` | 配置元数据定义（字段、类型、默认值） | ✅ 跟踪 |
| `local.yaml` | 实际配置值 + 自动生成的密钥 | ❌ 忽略 |
| `README.md` | 本说明文档 | ✅ 跟踪 |

## 🚀 快速开始

### 首次设置

```bash
# 1. 生成配置文件
./scripts/setup.sh

# 2. 编辑配置，设置 API keys
vim config/local.yaml

# 修改以下字段：
#   - openai.api_key: "sk-..."
#   - alpha_vantage.api_key: "..."
#   - tushare.token: "..." (可选)

# 3. 重新生成 .env
./scripts/setup.sh
```

### 配置文件生成流程

```
config.schema.yaml → config/local.yaml → backend/.env
   (元数据定义)       (实际配置)        (环境变量)
   [Git 跟踪]        [Git 忽略]        [Git 忽略]
```

## 📝 添加新配置

### 步骤 1: 编辑 schema

编辑 `config.schema.yaml`，添加字段定义：

**普通字段**:
```yaml
- section: my_service.timeout
  default: 30
  description: "服务超时时间（秒）"
```

**密钥字段**（自动生成）:
```yaml
- section: my_service.secret_key
  type: secret
  auto_generate: true
  description: "服务密钥（自动生成）"
```

### 步骤 2: 重新生成配置

```bash
./scripts/setup.sh
```

系统会：
1. 自动生成 `config/local.yaml`（保留所有现有值）
2. 为新的 secret 字段生成密钥
3. 更新 `backend/.env`

### 步骤 3: 更新代码（如需要）

如果需要在代码中使用新配置：

1. **更新 `backend/app/config.py`**:
```python
class Settings(BaseSettings):
    # ...
    my_service_timeout: int = Field(default=30, description="服务超时时间")
    my_service_secret_key: str = Field(..., description="服务密钥")
```

2. **更新 `scripts/lib/generate_env.py` 的 ENV_MAPPING**:
```python
ENV_MAPPING = {
    # ...
    'my_service.timeout': 'MY_SERVICE_TIMEOUT',
    'my_service.secret_key': 'MY_SERVICE_SECRET_KEY',
}
```

3. **重新生成 .env**:
```bash
./scripts/setup.sh
```

## 🔐 密钥管理

### 自动生成的密钥

标记为 `type: secret` 和 `auto_generate: true` 的字段会：
- **首次运行**: 自动生成 32 字符的安全随机密钥
- **后续运行**: 保留现有密钥，不会重新生成

当前自动生成的密钥：
- `app.secret_key` - 应用密钥
- `jwt.secret_key` - JWT 签名密钥

### 手动设置的密钥

需要手动在 `config/local.yaml` 中设置：
- `openai.api_key` - OpenAI API Key
- `alpha_vantage.api_key` - Alpha Vantage API Key
- `tushare.token` - Tushare Token（可选）

## 📊 配置结构

当前配置分为以下部分：

| 分类 | 字段数 | 说明 |
|------|--------|------|
| 应用配置 | 4 | app.* |
| 数据库配置 | 2 | database.* |
| Redis 配置 | 2 | redis.* |
| Qdrant 配置 | 2 | qdrant.* |
| JWT 配置 | 4 | jwt.* |
| CORS 配置 | 1 | cors.* |
| OpenAI API | 2 | openai.* |
| Alpha Vantage | 1 | alpha_vantage.* |
| Tushare API | 1 | tushare.* |
| Celery 配置 | 2 | celery.* |
| 日志配置 | 2 | log.* |
| 数据目录 | 1 | data.* |
| 语言配置 | 1 | i18n.* |
| 速率限制 | 2 | rate_limit.* |

## 🔄 配置更新流程

### 修改现有配置

```bash
# 1. 编辑配置
vim config/local.yaml

# 2. 重新生成 .env
./scripts/setup.sh

# 3. 重启服务
docker compose restart
cd backend && uv run python -m app.server
```

### 环境间配置

不同环境可以使用不同的配置文件：

```bash
# 开发环境（默认）
cp config/local.yaml config/local.dev.yaml

# 生产环境
cp config/local.yaml config/local.prod.yaml
# 编辑 local.prod.yaml，设置生产配置
# 修改 scripts/lib/generate_env.py 读取不同文件
```

## 🛡️ 安全性

### ✅ 安全实践

1. **密钥文件不提交 Git**:
   - `config/local.yaml` 已添加到 `.gitignore`
   - `backend/.env` 已添加到 `.gitignore`

2. **自动生成的密钥**:
   - 使用 `secrets` 模块生成
   - 32 字符长度，包含字母和数字
   - 加密安全的随机数生成器

3. **配置分离**:
   - Schema（元数据）可以公开
   - 实际值（密钥）不公开

### ❌ 注意事项

1. **不要提交 `config/local.yaml`** - 包含真实的 API keys
2. **不要在 schema 中写入真实密钥** - schema 文件会提交到 git
3. **定期轮换密钥** - 特别是生产环境
4. **备份配置文件** - `local.yaml` 是唯一保存密钥的地方

## 🔧 故障排除

### 问题: PyYAML 未安装

```bash
pip install pyyaml
```

### 问题: 权限错误

```bash
chmod +x scripts/setup.sh
chmod +x scripts/lib/*.py
```

### 问题: 配置未生效

```bash
# 1. 检查配置是否正确生成
cat config/local.yaml

# 2. 重新生成 .env
./scripts/setup.sh

# 3. 检查 .env
cat backend/.env

# 4. 重启服务
docker compose restart
```

### 问题: 密钥丢失

如果不小心删除了 `config/local.yaml`：

```bash
# 重新生成（会生成新的密钥！）
./scripts/setup.sh

# 如果有备份，恢复它
cp config/local.yaml.backup config/local.yaml
./scripts/setup.sh
```

## 📚 更多信息

- [Web UI 架构文档](../docs/web-ui-architecture.md)
- [开发文档](../docs/DEVELOPMENT.md)
- [后端 README](../backend/README.md)

---

最后更新: 2025-11-19
