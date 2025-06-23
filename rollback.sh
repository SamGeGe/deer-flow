#!/bin/bash

echo "🔙 DeerFlow 回滚脚本"
echo "=================="

# 检查备份文件
if [ ! -f "docker-compose.yml.backup" ]; then
    echo "❌ 错误：未找到docker-compose.yml备份文件"
    exit 1
fi

echo "⚠️  这将恢复到使用nginx之前的配置："
echo "- 前端端口: 4051"
echo "- 后端端口: 9050"
echo "- 需要硬编码IP地址"
echo ""

read -p "确定要回滚吗？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 回滚已取消"
    exit 1
fi

echo "🔄 停止当前服务..."
docker compose down

echo "📁 恢复配置文件..."
cp docker-compose.yml.backup docker-compose.yml

if [ -f ".env.backup" ]; then
    cp .env.backup .env
    echo "✅ .env文件已恢复"
else
    echo "⚠️  .env备份不存在，请手动检查API URL配置"
fi

echo "🏗️  重新构建服务..."
docker compose build

echo "🚀 启动服务..."
docker compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "🔍 检查服务状态..."
docker compose ps

echo ""
echo "✅ 回滚完成！"
echo "📱 前端访问: http://YOUR_PUBLIC_IP:4051"
echo "🔧 后端API: http://YOUR_PUBLIC_IP:9050"
echo "📝 记得更新.env中的NEXT_PUBLIC_API_URL为完整地址" 