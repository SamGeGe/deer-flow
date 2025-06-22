#!/bin/bash

# DeerFlow 项目清理脚本
# 删除不必要的文件，但保持项目可以正常运行

echo "🧹 DeerFlow 项目清理脚本"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计算清理前的大小
echo -e "\n📊 清理前项目大小:"
du -sh . | head -1

# 1. 删除 Python 缓存文件
echo -e "\n${BLUE}🐍 清理 Python 缓存文件...${NC}"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
echo -e "${GREEN}✅ Python 缓存文件已清理${NC}"

# 2. 删除系统缓存文件
echo -e "\n${BLUE}💻 清理系统缓存文件...${NC}"
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null
find . -name "desktop.ini" -delete 2>/dev/null
echo -e "${GREEN}✅ 系统缓存文件已清理${NC}"

# 3. 删除前端构建缓存
echo -e "\n${BLUE}🌐 清理前端构建缓存...${NC}"
if [ -d "web/.next" ]; then
    rm -rf web/.next
    echo -e "${GREEN}✅ Next.js 构建缓存已清理${NC}"
else
    echo -e "${YELLOW}⚠️  Next.js 构建缓存不存在${NC}"
fi

# 4. 删除临时文件
echo -e "\n${BLUE}📄 清理临时文件...${NC}"
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null
find . -name "*.log" -delete 2>/dev/null
find . -name "*.bak" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null
echo -e "${GREEN}✅ 临时文件已清理${NC}"

# 5. 清理输出目录
echo -e "\n${BLUE}📁 清理输出目录...${NC}"
if [ -d "outputs" ]; then
    rm -rf outputs/*
    echo -e "${GREEN}✅ 输出目录已清理${NC}"
else
    echo -e "${YELLOW}⚠️  输出目录不存在${NC}"
fi

# 6. 删除不必要的文档文件（保留重要的）
echo -e "\n${BLUE}📚 清理多余的文档文件...${NC}"

# 删除的文档文件列表
unnecessary_docs=(
    "FIXES_SUMMARY.md"
    "CONFIGURATION_OPTIMIZATION.md" 
    "MIGRATION_CHECKLIST.md"
    "README_TAVILY_SETUP.md"
    "test_fix.py"
)

for file in "${unnecessary_docs[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo -e "${GREEN}✅ 删除: $file${NC}"
    fi
done

# 7. 清理 IDE 和编辑器文件
echo -e "\n${BLUE}💡 清理 IDE 和编辑器文件...${NC}"
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".idea" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.swp" -delete 2>/dev/null
find . -name "*.swo" -delete 2>/dev/null
echo -e "${GREEN}✅ IDE 和编辑器文件已清理${NC}"

# 8. 清理 Git 相关（如果不是 Git 仓库）
echo -e "\n${BLUE}🔧 检查 Git 状态...${NC}"
if [ ! -d ".git" ]; then
    # 删除 Git 相关文件
    rm -f .gitignore
    echo -e "${GREEN}✅ 非 Git 仓库，已删除 .gitignore${NC}"
else
    echo -e "${YELLOW}⚠️  这是 Git 仓库，保留 Git 文件${NC}"
fi

# 9. 可选：删除开发依赖（需要用户确认）
echo -e "\n${BLUE}🔍 检查可选清理项...${NC}"

# 检查是否要删除 node_modules（用户选择）
if [ -d "web/node_modules" ]; then
    echo -e "${YELLOW}💡 发现 web/node_modules (629M)${NC}"
    echo -e "${YELLOW}   可以删除并在需要时重新安装 (pnpm install)${NC}"
    echo -e "${YELLOW}   这将显著减少项目大小${NC}"
fi

# 检查是否要删除 .venv（用户选择）
if [ -d ".venv" ]; then
    echo -e "${YELLOW}💡 发现 .venv 虚拟环境${NC}"
    echo -e "${YELLOW}   可以删除并在需要时重新创建 (uv sync)${NC}"
fi

# 10. 计算清理后的大小
echo -e "\n📊 清理后项目大小:"
du -sh . | head -1

echo -e "\n${GREEN}🎉 清理完成！${NC}"
echo -e "\n📋 清理总结:"
echo -e "✅ Python 缓存文件 (__pycache__, *.pyc)"
echo -e "✅ 系统缓存文件 (.DS_Store 等)"
echo -e "✅ 前端构建缓存 (.next)"
echo -e "✅ 临时文件 (*.tmp, *.log, *.bak)"
echo -e "✅ 输出目录内容"
echo -e "✅ 多余的文档文件"
echo -e "✅ IDE 和编辑器文件"

echo -e "\n💡 进一步减少大小的选项:"
echo -e "   1. 删除 web/node_modules (629M) - 可用 'cd web && pnpm install' 恢复"
echo -e "   2. 删除 .venv - 可用 'uv sync' 恢复"
echo -e "   3. 删除 assets/ 目录 (152K) - 如果不需要示例图片"

echo -e "\n${BLUE}🚀 项目仍可正常运行:${NC}"
echo -e "   开发模式: ./bootstrap.sh --dev"
echo -e "   Docker 模式: docker-compose up -d" 