#!/bin/bash
#
# TradingAgents 项目设置脚本
#
# 功能:
#   1. 检查系统依赖（Docker, Python, Node.js, uv）
#   2. 生成配置文件（config/local.yaml, backend/.env）
#   3. 安装 Python 依赖
#   4. 安装 Node.js 依赖
#   5. 启动 Docker 服务（TimescaleDB, Redis, Qdrant）
#   6. 初始化数据库（Alembic migrations）
#   7. 创建必要的目录
#   8. 验证配置
#
# 使用:
#   ./scripts/setup.sh [options]
#
# 选项:
#   --skip-deps        跳过依赖安装
#   --skip-docker      跳过 Docker 服务启动
#   --skip-db          跳过数据库初始化
#   --config-only      仅生成配置文件
#   -h, --help         显示帮助信息
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 确定脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 默认选项
SKIP_DEPS=false
SKIP_DOCKER=false
SKIP_DB=false
CONFIG_ONLY=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-db)
            SKIP_DB=true
            shift
            ;;
        --config-only)
            CONFIG_ONLY=true
            shift
            ;;
        -h|--help)
            echo "使用方法: $0 [options]"
            echo ""
            echo "选项:"
            echo "  --skip-deps        跳过依赖安装"
            echo "  --skip-docker      跳过 Docker 服务启动"
            echo "  --skip-db          跳过数据库初始化"
            echo "  --config-only      仅生成配置文件"
            echo "  -h, --help         显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  $0                  # 完整设置"
            echo "  $0 --config-only    # 仅生成配置"
            echo "  $0 --skip-docker    # 跳过 Docker（手动启动）"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            echo "使用 --help 查看帮助"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      TradingAgents Project Setup              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================
# 步骤 1: 检查系统依赖
# ============================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: 检查系统依赖${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 已安装"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 未安装"
        return 1
    fi
}

DEPS_OK=true

# 检查 Python 3
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "    版本: ${PYTHON_VERSION}"
else
    DEPS_OK=false
fi

# 检查 Docker
if ! $SKIP_DOCKER; then
    if check_command docker; then
        DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
        echo -e "    版本: ${DOCKER_VERSION}"
    else
        DEPS_OK=false
    fi

    # 检查 Docker Compose
    if check_command docker-compose || docker compose version &> /dev/null; then
        if docker compose version &> /dev/null; then
            COMPOSE_VERSION=$(docker compose version --short)
        else
            COMPOSE_VERSION=$(docker-compose --version | awk '{print $3}' | tr -d ',')
        fi
        echo -e "  ${GREEN}✓${NC} docker compose 已安装"
        echo -e "    版本: ${COMPOSE_VERSION}"
    else
        DEPS_OK=false
    fi
fi

# 检查 uv (可选)
if check_command uv; then
    UV_VERSION=$(uv --version | awk '{print $2}')
    echo -e "    版本: ${UV_VERSION}"
else
    echo -e "  ${YELLOW}⚠${NC}  uv 未安装（可选，推荐用于 Python 依赖管理）"
    echo -e "    安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# 检查 Node.js (可选)
if check_command node; then
    NODE_VERSION=$(node --version)
    echo -e "    版本: ${NODE_VERSION}"
else
    echo -e "  ${YELLOW}⚠${NC}  Node.js 未安装（前端开发需要）"
fi

# 检查 pnpm (可选)
if check_command pnpm; then
    PNPM_VERSION=$(pnpm --version)
    echo -e "  ${GREEN}✓${NC} pnpm 已安装"
    echo -e "    版本: ${PNPM_VERSION}"
else
    echo -e "  ${YELLOW}⚠${NC}  pnpm 未安装（前端开发需要）"
    echo -e "    安装: npm install -g pnpm"
fi

if ! $DEPS_OK; then
    echo ""
    echo -e "${RED}❌ 缺少必要的系统依赖，请先安装${NC}"
    exit 1
fi

echo ""

# ============================================================
# 步骤 2: 生成配置文件
# ============================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: 生成配置文件${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 PyYAML
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PyYAML 未安装，正在安装...${NC}"
    pip install pyyaml
fi

# 生成 config/local.yaml
echo -e "${BLUE}➜${NC} 生成 config/local.yaml"
python3 "$SCRIPT_DIR/lib/generate_from_schema.py"
echo ""

# 生成 backend/.env
echo -e "${BLUE}➜${NC} 生成 backend/.env"
python3 "$SCRIPT_DIR/lib/generate_env.py"
echo ""

if $CONFIG_ONLY; then
    echo -e "${GREEN}✅ 配置文件生成完成！${NC}"
    echo ""
    echo -e "下一步: 编辑 config/local.yaml 设置 API keys"
    exit 0
fi

# ============================================================
# 步骤 3: 创建必要的目录
# ============================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: 创建必要的目录${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

mkdir -p "$PROJECT_ROOT/backend/logs"
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/backend/alembic/versions"

echo -e "  ${GREEN}✓${NC} backend/logs/"
echo -e "  ${GREEN}✓${NC} data/"
echo -e "  ${GREEN}✓${NC} backend/alembic/versions/"
echo ""

# ============================================================
# 步骤 4: 安装 Python 依赖
# ============================================================
if ! $SKIP_DEPS; then
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Step 4: 安装 Python 依赖${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    cd "$PROJECT_ROOT/backend"

    if command -v uv &> /dev/null; then
        echo -e "${BLUE}➜${NC} 使用 uv 安装依赖..."
        uv sync
    else
        echo -e "${BLUE}➜${NC} 使用 pip 安装依赖..."
        pip install -r requirements.txt 2>/dev/null || echo -e "${YELLOW}⚠${NC}  requirements.txt 未找到"
    fi

    cd "$PROJECT_ROOT"
    echo ""
fi

# ============================================================
# 步骤 5: 启动 Docker 服务
# ============================================================
if ! $SKIP_DOCKER; then
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Step 5: 启动 Docker 服务${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    echo -e "${BLUE}➜${NC} 启动 TimescaleDB, Redis, Qdrant..."

    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi

    echo ""
    echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
    sleep 5

    # 检查服务状态
    echo -e "${BLUE}➜${NC} 检查服务状态..."
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
    echo ""
fi

# ============================================================
# 步骤 6: 初始化数据库
# ============================================================
if ! $SKIP_DB && ! $SKIP_DOCKER; then
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Step 6: 初始化数据库${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    cd "$PROJECT_ROOT/backend"

    echo -e "${BLUE}➜${NC} 运行 Alembic migrations..."

    # 等待数据库启动
    echo -e "${YELLOW}⏳ 等待 TimescaleDB 启动...${NC}"
    sleep 3

    # 运行迁移
    if command -v uv &> /dev/null; then
        uv run alembic upgrade head
    else
        alembic upgrade head
    fi

    echo -e "${GREEN}✓${NC} 数据库初始化完成"

    cd "$PROJECT_ROOT"
    echo ""
fi

# ============================================================
# 步骤 7: 验证配置
# ============================================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 7: 验证配置${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查 API keys 是否已设置
CONFIG_FILE="$PROJECT_ROOT/config/local.yaml"
WARNINGS=()

check_api_key() {
    local key=$1
    local name=$2
    local value=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))$key)" 2>/dev/null)

    if [[ $value == "your-"* ]] || [[ -z $value ]]; then
        WARNINGS+=("$name 未设置")
        return 1
    fi
    return 0
}

if check_api_key "['openai']['api_key']" "OpenAI API Key"; then
    echo -e "  ${GREEN}✓${NC} OpenAI API Key 已设置"
else
    echo -e "  ${YELLOW}⚠${NC}  OpenAI API Key 未设置"
fi

if check_api_key "['alpha_vantage']['api_key']" "Alpha Vantage API Key"; then
    echo -e "  ${GREEN}✓${NC} Alpha Vantage API Key 已设置"
else
    echo -e "  ${YELLOW}⚠${NC}  Alpha Vantage API Key 未设置"
fi

if check_api_key "['tushare']['token']" "Tushare Token"; then
    echo -e "  ${GREEN}✓${NC} Tushare Token 已设置"
else
    echo -e "  ${YELLOW}⚠${NC}  Tushare Token 未设置（可选）"
fi

echo ""

# ============================================================
# 完成
# ============================================================
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║             Setup Complete! 🎉                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  注意事项:${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo -e "  • $warning"
    done
    echo ""
    echo -e "${CYAN}请编辑 config/local.yaml 设置 API keys，然后重新运行:${NC}"
    echo -e "  ${BLUE}./scripts/setup.sh --config-only${NC}"
    echo ""
fi

echo -e "${GREEN}📁 生成的文件:${NC}"
echo -e "  • config/local.yaml"
echo -e "  • backend/.env"
echo ""

echo -e "${GREEN}🚀 下一步:${NC}"
echo ""
echo -e "${CYAN}1. 启动后端服务:${NC}"
echo -e "   cd backend"
echo -e "   uv run python -m app.server"
echo ""
echo -e "${CYAN}2. 访问 API 文档:${NC}"
echo -e "   http://localhost:8005/api/docs"
echo ""

if command -v pnpm &> /dev/null; then
    echo -e "${CYAN}3. 启动前端（可选）:${NC}"
    echo -e "   cd frontend"
    echo -e "   pnpm install"
    echo -e "   pnpm dev"
    echo ""
    echo -e "   访问: http://localhost:3005"
    echo ""
fi

echo -e "${CYAN}4. 查看服务状态:${NC}"
echo -e "   docker compose ps"
echo ""

echo -e "${GREEN}✨ 愉快开发！${NC}"
echo ""
