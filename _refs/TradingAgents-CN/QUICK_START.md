# 快速启动指南

## macOS 一键启动

### 使用方法

#### 1. 默认启动（推荐）

```bash
./quick-start-mac.sh
```

这将：
- ✓ 启动所有 Docker 服务
- ✓ 自动健康检查
- ✓ 创建默认管理员账号（admin/admin123）
- ✓ 显示访问信息

#### 2. 自定义管理员账号

```bash
./quick-start-mac.sh --username myuser --password mypass123 --email user@example.com
```

#### 3. 查看帮助

```bash
./quick-start-mac.sh --help
```

### 脚本功能

| 功能 | 说明 |
|------|------|
| **服务启动** | 自动启动 MongoDB、Redis、Backend、Frontend、Nginx |
| **健康检查** | 等待所有服务就绪后再继续 |
| **账号创建** | 自动创建管理员账号（如果不存在） |
| **状态显示** | 显示所有容器运行状态 |
| **错误处理** | 优雅的错误提示和退出 |

### 访问地址

启动成功后，访问以下地址：

- **前端应用**: http://localhost:8004
- **API 文档**: http://localhost:8004/api/docs
- **健康检查**: http://localhost:8004/api/health

### 默认登录信息

- **用户名**: admin
- **密码**: admin123

**重要提示**: 首次登录后请立即修改密码！

### 故障排除

#### 端口冲突

如果遇到端口冲突，请检查：

```bash
# 检查端口占用
lsof -i :8004  # Nginx
lsof -i :27017 # MongoDB
lsof -i :6384  # Redis
```

#### 容器无法启动

查看日志：

```bash
docker-compose -f docker-compose.hub.nginx.arm.yml logs
```

#### 清理重启

```bash
# 停止所有服务
docker-compose -f docker-compose.hub.nginx.arm.yml down

# 清理数据卷（谨慎使用，会删除所有数据）
docker-compose -f docker-compose.hub.nginx.arm.yml down -v

# 重新启动
./quick-start-mac.sh
```

### 停止服务

```bash
docker-compose -f docker-compose.hub.nginx.arm.yml down
```

### 查看服务状态

```bash
docker-compose -f docker-compose.hub.nginx.arm.yml ps
```

### 查看实时日志

```bash
# 所有服务
docker-compose -f docker-compose.hub.nginx.arm.yml logs -f

# 特定服务
docker-compose -f docker-compose.hub.nginx.arm.yml logs -f backend
docker-compose -f docker-compose.hub.nginx.arm.yml logs -f frontend
```

## 系统要求

- macOS (Apple Silicon 或 Intel)
- Docker Desktop 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 下一步

1. 访问 http://localhost:8004
2. 使用 admin/admin123 登录
3. 修改默认密码
4. 配置 LLM API 密钥（设置 → 配置管理）
5. 同步股票数据（系统管理 → 数据同步）
6. 开始分析！

## 相关文档

- [Docker 部署指南](docs/guides/docker-deployment-guide.md)
- [配置说明](docs/configuration_guide.md)
- [使用指南](https://mp.weixin.qq.com/s/ppsYiBncynxlsfKFG8uEbw)
