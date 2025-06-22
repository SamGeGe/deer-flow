#!/bin/bash

# DeerFlow 部署检查脚本
# 用于验证项目是否能在新环境中正常运行

echo "🦌 DeerFlow 部署检查脚本"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "✅ $1: ${GREEN}已安装${NC}"
        return 0
    else
        echo -e "❌ $1: ${RED}未安装${NC}"
        return 1
    fi
}

check_version() {
    local cmd="$1"
    local version_cmd="$2"
    local min_version="$3"
    
    if command -v "$cmd" &> /dev/null; then
        local current_version=$($version_cmd 2>/dev/null | head -1)
        echo -e "✅ $cmd: ${GREEN}$current_version${NC}"
        return 0
    else
        echo -e "❌ $cmd: ${RED}未安装 (需要 $min_version 或更高版本)${NC}"
        return 1
    fi
}

# 系统要求检查
echo -e "\n📋 系统要求检查"
echo "----------------"

# 检查 Python
check_version "python3" "python3 --version" "3.12+"

# 检查 uv
check_version "uv" "uv --version" "0.7+"

# 检查 Node.js
check_version "node" "node --version" "18+"

# 检查 pnpm
check_version "pnpm" "pnpm --version" "8+"

# 检查 Docker (可选)
echo -e "\n🐳 Docker 检查 (可选)"
echo "-------------------"
check_command "docker"
check_command "docker-compose"

# 项目文件检查
echo -e "\n📁 项目文件检查"
echo "----------------"

required_files=(
    "pyproject.toml"
    "uv.lock"
    "conf.yaml"
    "env.example"
    "bootstrap.sh"
    "docker-compose.yml"
    "web/package.json"
    "web/pnpm-lock.yaml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "✅ $file: ${GREEN}存在${NC}"
    else
        echo -e "❌ $file: ${RED}缺失${NC}"
    fi
done

# 依赖安装检查
echo -e "\n📦 依赖安装检查"
echo "----------------"

# 检查 Python 依赖
echo "检查 Python 依赖..."
if uv sync --locked > /dev/null 2>&1; then
    echo -e "✅ Python 依赖: ${GREEN}已安装${NC}"
else
    echo -e "❌ Python 依赖: ${RED}安装失败${NC}"
    echo "请运行: uv sync --locked"
fi

# 检查前端依赖
echo "检查前端依赖..."
cd web
if [ -d "node_modules" ] && [ -f "node_modules/.pnpm/lock.yaml" ]; then
    echo -e "✅ 前端依赖: ${GREEN}已安装${NC}"
else
    echo -e "⚠️  前端依赖: ${YELLOW}需要安装${NC}"
    echo "请运行: cd web && pnpm install"
fi
cd ..

# 配置文件检查
echo -e "\n⚙️  配置文件检查"
echo "----------------"

if [ -f ".env" ]; then
    echo -e "✅ .env: ${GREEN}存在${NC}"
    
    # 检查 Tavily API 密钥
    if grep -q "TAVILY_API_KEY=tvly-" .env && ! grep -q "TAVILY_API_KEY=tvly-xxx" .env; then
        echo -e "✅ Tavily API: ${GREEN}已配置${NC}"
    else
        echo -e "⚠️  Tavily API: ${YELLOW}未配置 (将使用 DuckDuckGo 作为回退)${NC}"
    fi
else
    echo -e "⚠️  .env: ${YELLOW}不存在 (运行 bootstrap.sh 时会自动创建)${NC}"
fi

# 服务启动测试
echo -e "\n🚀 服务启动测试"
echo "----------------"

echo "测试后端服务器启动..."
uv run python server.py --port 9001 &
SERVER_PID=$!
sleep 3

if curl -s http://localhost:9001/api/config > /dev/null 2>&1; then
    echo -e "✅ 后端服务: ${GREEN}启动成功${NC}"
else
    echo -e "❌ 后端服务: ${RED}启动失败${NC}"
fi

# 停止后端
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

# 总结
echo -e "\n📊 检查总结"
echo "============"

echo "如果所有检查都通过，您可以使用以下命令启动 DeerFlow:"
echo ""
echo "开发模式:"
echo "  ./bootstrap.sh --dev"
echo "  访问: http://localhost:9000"
echo ""
echo "Docker 模式:"
echo "  docker-compose up -d"
echo "  访问: http://localhost:4051"
echo ""
echo "如果遇到问题，请查看 README.md 或 docs/ 目录中的文档。" 