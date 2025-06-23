#!/bin/bash

# 流式响应修复更新脚本

set -e

echo "🔧 更新流式响应修复..."
echo "========================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker服务
log_info "检查Docker服务状态..."
if ! docker compose ps | grep -q "Up"; then
    log_error "Docker服务未运行，请先启动服务"
    exit 1
fi

# 重新构建后端服务
log_info "重新构建后端服务..."
docker compose build backend

# 重启服务
log_info "重启服务..."
docker compose restart

# 等待服务启动
log_info "等待服务启动..."
sleep 15

# 检查服务状态
log_info "检查服务状态..."
if docker compose ps | grep -q "Up"; then
    log_success "服务更新成功！"
    
    echo ""
    echo "🎉 流式响应修复完成！"
    echo "======================"
    echo ""
    echo "修复内容："
    echo "✅ 优化nginx流式响应配置"
    echo "✅ 修复后端agent访问错误"
    echo "✅ 增强错误处理机制"
    echo "✅ 优化JSON序列化"
    echo ""
    echo "📱 访问地址："
    echo "   http://localhost:4051"
    echo ""
    echo "🔧 如果仍有问题，请查看日志："
    echo "   docker compose logs -f backend"
    
else
    log_error "服务启动失败"
    docker compose logs --tail=20
    exit 1
fi 