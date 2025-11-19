#!/bin/bash
#
# TradingAgents 配置生成脚本
#
# 功能:
#   1. 从 config.schema.yaml 生成 config/local.yaml
#   2. 从 config/local.yaml 生成 backend/.env
#
# 使用:
#   ./scripts/setup.sh
#

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 确定脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  TradingAgents Configuration Setup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3 未安装${NC}"
    exit 1
fi

# 检查 PyYAML
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PyYAML 未安装，正在安装...${NC}"
    pip install pyyaml
fi

# 步骤 1: 生成 config/local.yaml
echo -e "${GREEN}Step 1/2: 生成 config/local.yaml${NC}"
echo "----------------------------------------"
python3 "$SCRIPT_DIR/lib/generate_from_schema.py"
echo ""

# 步骤 2: 生成 backend/.env
echo -e "${GREEN}Step 2/2: 生成 backend/.env${NC}"
echo "----------------------------------------"
python3 "$SCRIPT_DIR/lib/generate_env.py"
echo ""

# 完成
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ 配置生成完成！${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "📁 生成的文件:"
echo "  - config/local.yaml    (实际配置 + 自动生成的密钥)"
echo "  - backend/.env         (环境变量文件)"
echo ""
echo "📝 下一步:"
echo "  1. 编辑 config/local.yaml，设置 API keys:"
echo "     - openai.api_key"
echo "     - alpha_vantage.api_key"
echo "     - tushare.token (可选)"
echo ""
echo "  2. 重新运行此脚本更新 .env:"
echo "     ./scripts/setup.sh"
echo ""
echo "  3. 启动服务:"
echo "     docker compose up -d"
echo "     cd backend && uv run python -m app.server"
echo ""
