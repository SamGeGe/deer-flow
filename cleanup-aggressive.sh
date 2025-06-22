#!/bin/bash

# DeerFlow 激进清理脚本
# 最大化减少项目大小，但需要重新安装依赖才能运行

echo "🔥 DeerFlow 激进清理脚本"
echo "=========================="
echo "⚠️  警告：此脚本将删除依赖文件，需要重新安装才能运行项目"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 询问用户确认
read -p "是否继续？(y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "取消清理"
    exit 0
fi

# 计算清理前的大小
echo -e "\n📊 清理前项目大小:"
du -sh . | head -1

# 1. 运行基础清理
echo -e "\n${BLUE}🧹 运行基础清理...${NC}"
./cleanup.sh > /dev/null 2>&1
echo -e "${GREEN}✅ 基础清理完成${NC}"

# 2. 删除 node_modules
echo -e "\n${BLUE}📦 删除前端依赖 (node_modules)...${NC}"
if [ -d "web/node_modules" ]; then
    rm -rf web/node_modules
    echo -e "${GREEN}✅ 已删除 web/node_modules (629M)${NC}"
    echo -e "${YELLOW}💡 恢复命令: cd web && pnpm install${NC}"
else
    echo -e "${YELLOW}⚠️  node_modules 不存在${NC}"
fi

# 3. 删除 Python 虚拟环境
echo -e "\n${BLUE}🐍 删除 Python 虚拟环境 (.venv)...${NC}"
if [ -d ".venv" ]; then
    rm -rf .venv
    echo -e "${GREEN}✅ 已删除 .venv${NC}"
    echo -e "${YELLOW}💡 恢复命令: uv sync${NC}"
else
    echo -e "${YELLOW}⚠️  .venv 不存在${NC}"
fi

# 4. 删除锁文件（可选，但会强制重新解析依赖）
echo -e "\n${BLUE}🔒 处理锁文件...${NC}"
read -p "是否删除锁文件以减少大小？(删除后首次安装会慢一些) (y/N): " lock_confirm
if [[ $lock_confirm == [yY] ]]; then
    if [ -f "uv.lock" ]; then
        rm uv.lock
        echo -e "${GREEN}✅ 已删除 uv.lock (384K)${NC}"
    fi
    if [ -f "web/pnpm-lock.yaml" ]; then
        rm web/pnpm-lock.yaml
        echo -e "${GREEN}✅ 已删除 pnpm-lock.yaml (316K)${NC}"
    fi
    echo -e "${YELLOW}💡 恢复时会重新生成锁文件${NC}"
else
    echo -e "${YELLOW}⚠️  保留锁文件${NC}"
fi

# 5. 删除示例文件
echo -e "\n${BLUE}📄 删除示例文件...${NC}"
if [ -d "examples" ]; then
    rm -rf examples
    echo -e "${GREEN}✅ 已删除 examples/ (92K)${NC}"
else
    echo -e "${YELLOW}⚠️  examples 目录不存在${NC}"
fi

# 6. 删除资源文件
echo -e "\n${BLUE}🖼️  删除资源文件...${NC}"
read -p "是否删除 assets 目录？(包含示例图片) (y/N): " assets_confirm
if [[ $assets_confirm == [yY] ]]; then
    if [ -d "assets" ]; then
        rm -rf assets
        echo -e "${GREEN}✅ 已删除 assets/ (152K)${NC}"
    else
        echo -e "${YELLOW}⚠️  assets 目录不存在${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  保留 assets 目录${NC}"
fi

# 7. 删除测试文件
echo -e "\n${BLUE}🧪 删除测试文件...${NC}"
read -p "是否删除测试文件？(y/N): " test_confirm
if [[ $test_confirm == [yY] ]]; then
    if [ -d "tests" ]; then
        rm -rf tests
        echo -e "${GREEN}✅ 已删除 tests/ (260K)${NC}"
    else
        echo -e "${YELLOW}⚠️  tests 目录不存在${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  保留测试文件${NC}"
fi

# 8. 删除前端文档
echo -e "\n${BLUE}📚 删除前端文档...${NC}"
if [ -d "web/docs" ]; then
    rm -rf web/docs
    echo -e "${GREEN}✅ 已删除 web/docs/ (24K)${NC}"
else
    echo -e "${YELLOW}⚠️  web/docs 不存在${NC}"
fi

# 9. 删除额外的 README 文件
echo -e "\n${BLUE}📖 清理多余的 README 文件...${NC}"
if [ -f "README_zh.md" ]; then
    rm README_zh.md
    echo -e "${GREEN}✅ 已删除 README_zh.md (20K)${NC}"
fi
if [ -f "web/README.md" ]; then
    rm web/README.md
    echo -e "${GREEN}✅ 已删除 web/README.md${NC}"
fi

# 10. 计算清理后的大小
echo -e "\n📊 清理后项目大小:"
du -sh . | head -1

# 计算节省的空间
echo -e "\n${GREEN}🎉 激进清理完成！${NC}"

echo -e "\n📋 已删除的内容:"
echo -e "✅ 所有缓存和临时文件"
echo -e "✅ 前端依赖 (node_modules)"
echo -e "✅ Python 虚拟环境 (.venv)"
echo -e "✅ 示例文件 (examples/)"
echo -e "✅ 前端文档 (web/docs/)"
echo -e "✅ 多余的 README 文件"

echo -e "\n🔧 恢复项目运行的步骤:"
echo -e "1. 安装 Python 依赖: ${BLUE}uv sync${NC}"
echo -e "2. 安装前端依赖: ${BLUE}cd web && pnpm install${NC}"
echo -e "3. 启动项目: ${BLUE}./bootstrap.sh --dev${NC} 或 ${BLUE}docker-compose up -d${NC}"

echo -e "\n💡 提示:"
echo -e "- 首次安装可能需要更长时间（特别是如果删除了锁文件）"
echo -e "- 所有核心功能保持不变"
echo -e "- 可以随时运行 ./check-deployment.sh 检查环境" 