#!/bin/bash

# 设置博查AI搜索引擎 API 密钥的脚本

if [ -z "$1" ]; then
    echo "用法: $0 <BOCHA_API_KEY>"
    echo ""
    echo "示例: $0 sk-your-api-key-here"
    echo ""
    echo "获取博查AI搜索 API 密钥:"
    echo "1. 访问 https://www.bochaai.com/"
    echo "2. 注册账户并获取 API 密钥"
    echo "3. 运行此脚本设置密钥"
    exit 1
fi

BOCHA_API_KEY="$1"

echo "正在设置博查AI搜索 API 密钥..."

# 设置环境变量 (当前会话)
export BOCHA_API_KEY="$BOCHA_API_KEY"

# 创建或更新 .env 文件
if [ -f .env ]; then
    # 如果 .env 文件存在，更新 BOCHA_API_KEY
    if grep -q "BOCHA_API_KEY=" .env; then
        # 更新现有的密钥
        sed -i.bak "s|BOCHA_API_KEY=.*|BOCHA_API_KEY=$BOCHA_API_KEY|" .env
        rm -f .env.bak
        echo "已更新 .env 文件中的 BOCHA_API_KEY"
    else
        # 添加新的密钥
        echo "BOCHA_API_KEY=$BOCHA_API_KEY" >> .env
        echo "已添加 BOCHA_API_KEY 到 .env 文件"
    fi
    
    # 同时设置搜索引擎为博查
    if grep -q "SEARCH_API=" .env; then
        sed -i.bak "s|SEARCH_API=.*|SEARCH_API=bocha|" .env
        rm -f .env.bak
        echo "已设置搜索引擎为博查AI"
    else
        echo "SEARCH_API=bocha" >> .env
        echo "已添加搜索引擎配置"
    fi
else
    # 创建新的 .env 文件，基于 env.example
    if [ -f env.example ]; then
        echo "基于 env.example 创建 .env 文件..."
        cp env.example .env
        
        # 更新博查密钥
        sed -i.bak "s|BOCHA_API_KEY=sk-xxx|BOCHA_API_KEY=$BOCHA_API_KEY|" .env
        # 确保搜索引擎设置为博查
        sed -i.bak "s|SEARCH_API=.*|SEARCH_API=bocha|" .env
        rm -f .env.bak
        
        echo "已创建 .env 文件并设置 BOCHA_API_KEY"
    else
        # 如果没有 env.example，创建基本的 .env 文件
        echo "创建基本的 .env 文件..."
        cat > .env << EOF
# Application Settings
DEBUG=True
APP_ENV=development

# docker build args
NEXT_PUBLIC_API_URL="http://localhost:8000/api"

AGENT_RECURSION_LIMIT=30

# Search Engine, Supported values: bocha (中文优化), tavily (recommended), duckduckgo, brave_search, arxiv
SEARCH_API=bocha
BOCHA_API_KEY=$BOCHA_API_KEY
TAVILY_API_KEY=tvly-xxx

# [!NOTE]
# For model settings and other configurations, please refer to docs/configuration_guide.md
EOF
        echo "已创建 .env 文件并设置 BOCHA_API_KEY"
    fi
fi

echo ""
echo "✅ 博查AI搜索 API 密钥设置完成！"
echo ""
echo "现在你可以使用以下命令启动 DeerFlow:"
echo ""
echo "Docker 模式:"
echo "  docker-compose up -d"
echo ""
echo "开发模式:"
echo "  ./bootstrap.sh -d"
echo ""
echo "系统将使用博查AI搜索引擎进行中文优化搜索，为您提供更准确的中文搜索结果。" 