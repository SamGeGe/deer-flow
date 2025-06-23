#!/bin/bash

echo "🦌 DeerFlow Nginx 部署脚本"
echo "=========================="

# 检查是否存在备份
if [ ! -f "docker-compose.yml.backup" ]; then
    echo "❌ 错误：未找到备份文件，请先运行备份"
    exit 1
fi

echo "📋 当前配置概览："
echo "- Nginx反向代理: 4051端口"
echo "- 前端: 通过nginx访问"
echo "- 后端API: 通过nginx的/api路径访问"
echo "- API URL: 相对路径 /api"
echo ""

# 询问用户是否继续
read -p "是否继续部署？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

echo "🔄 停止现有服务..."
docker compose down

echo "🏗️  重新构建服务..."
docker compose build

echo "🚀 启动新服务..."
docker compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "🔍 检查服务状态..."
docker compose ps

echo ""
echo "✅ 部署完成！"
echo "📱 访问地址: http://YOUR_PUBLIC_IP:4051"
echo "📊 Nginx状态: docker compose logs nginx"
echo "🔙 如需回滚: ./rollback.sh"
echo ""
echo "注意：现在只需要开放4051端口，不再需要单独的前后端端口" 