#!/bin/bash

# DeerFlow Linux 一键部署脚本
# 支持Ubuntu/Debian/CentOS/RHEL等主流Linux发行版

set -e  # 遇到错误立即退出

echo "🦌 DeerFlow Linux 一键部署脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检测系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        log_error "无法检测系统类型"
        exit 1
    fi
    log_info "检测到系统: $OS $VER"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "检测到root用户，建议使用普通用户运行"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 安装Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_success "Docker 已安装"
        return
    fi

    log_info "安装 Docker..."
    
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
            # 更新包索引
            sudo apt-get update
            
            # 安装必要的包
            sudo apt-get install -y \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release
            
            # 添加Docker官方GPG密钥
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # 添加Docker仓库
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
                $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # 安装Docker Engine
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"AlmaLinux"*)
            # 安装必要的包
            sudo yum install -y yum-utils
            
            # 添加Docker仓库
            sudo yum-config-manager \
                --add-repo \
                https://download.docker.com/linux/centos/docker-ce.repo
            
            # 安装Docker Engine
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        *)
            log_error "不支持的系统类型: $OS"
            log_info "请手动安装Docker: https://docs.docker.com/engine/install/"
            exit 1
            ;;
    esac
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 添加用户到docker组
    sudo usermod -aG docker $USER
    
    log_success "Docker 安装完成"
    log_warning "请重新登录以使docker组权限生效，或运行: newgrp docker"
}

# 安装Docker Compose（如果需要）
install_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        log_success "Docker Compose 已安装"
        return
    fi

    log_info "安装 Docker Compose..."
    
    # 下载最新版本的Docker Compose
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose 安装完成"
}

# 检查项目文件
check_project_files() {
    log_info "检查项目文件..."
    
    required_files=("docker-compose.yml" "Dockerfile" "pyproject.toml" "web/package.json")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    log_success "项目文件检查完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        log_info "创建 .env 文件..."
        cp env.example .env
        
        # 更新API URL为相对路径（适配nginx反向代理）
        sed -i 's|NEXT_PUBLIC_API_URL="http://localhost:8000/api"|NEXT_PUBLIC_API_URL="/api"|g' .env
        
        log_success ".env 文件创建完成"
    else
        log_success ".env 文件已存在"
    fi
    
    # 检查 conf.yaml 文件
    if [ ! -f "conf.yaml" ]; then
        if [ -f "conf.yaml.example" ]; then
            log_info "创建 conf.yaml 配置文件..."
            cp conf.yaml.example conf.yaml
            log_success "conf.yaml 文件已从模板创建"
            log_warning "请编辑 conf.yaml 文件配置您的 LLM 模型 API 密钥"
        else
            log_warning "未找到 conf.yaml 和 conf.yaml.example 文件"
        fi
        log_info "LLM 模型配置说明："
        log_info "  - 编辑 conf.yaml 文件配置 LLM 模型"
        log_info "  - 参考 docs/configuration_guide.md 获取详细配置指南"
        log_info "  - 支持 OpenAI、深度求索、通义千问、豆包等模型"
    else
        log_success "conf.yaml 配置文件已存在"
    fi
    
    log_success "环境配置完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    # 检查防火墙状态
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian UFW
        if sudo ufw status | grep -q "Status: active"; then
            log_info "配置 UFW 防火墙规则..."
            sudo ufw allow 4051/tcp comment "DeerFlow Frontend"
            log_success "UFW 防火墙规则已添加"
        fi
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        if sudo firewall-cmd --state &> /dev/null; then
            log_info "配置 firewalld 防火墙规则..."
            sudo firewall-cmd --permanent --add-port=4051/tcp
            sudo firewall-cmd --reload
            log_success "firewalld 防火墙规则已添加"
        fi
    else
        log_warning "未检测到防火墙，请手动开放端口 4051"
    fi
}

# 部署应用
deploy_application() {
    log_info "开始部署应用..."
    
    # 停止可能存在的旧容器
    if docker compose ps -q &> /dev/null; then
        log_info "停止现有容器..."
        docker compose down
    fi
    
    # 构建并启动服务
    log_info "构建 Docker 镜像..."
    docker compose build
    
    log_info "启动服务..."
    docker compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker compose ps | grep -q "Up"; then
        log_success "服务启动成功！"
    else
        log_error "服务启动失败，请检查日志"
        docker compose logs
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 DeerFlow 部署完成！"
    echo "======================="
    echo ""
    echo "📱 访问地址："
    echo "   前端界面: http://$(hostname -I | awk '{print $1}'):4051"
    echo "   本地访问: http://localhost:4051"
    echo ""
    echo "🔧 管理命令："
    echo "   查看状态: docker compose ps"
    echo "   查看日志: docker compose logs -f"
    echo "   重启服务: docker compose restart"
    echo "   停止服务: docker compose down"
    echo ""
    echo "📚 配置说明："
    echo "   - 编辑 .env 文件配置环境变量"
    echo "   - 编辑 conf.yaml 文件配置 LLM 模型"
    echo "   - 查看 docs/configuration_guide.md 获取详细配置指南"
    echo "   - 查看 docs/dependencies_guide.md 获取依赖管理说明"
    echo ""
    echo "🤖 LLM 模型："
    echo "   - 支持: OpenAI GPT-4o, 深度求索, 通义千问, 豆包等"
    echo "   - 配置文件: conf.yaml"
    echo "   - 获取 API 密钥后编辑配置文件即可使用"
    echo ""
    echo "🔍 搜索引擎："
    echo "   - 当前默认: 博查AI (中文优化搜索)"
    echo "   - 如需使用博查: ./set-bocha-key.sh your_api_key"
    echo "   - 如需使用Tavily: ./set-tavily-key.sh your_api_key"
    echo "   - 也支持: DuckDuckGo (无需API密钥), Brave Search, Arxiv"
    echo ""
    echo "⚠️  注意事项："
    echo "   - 确保防火墙开放了4051端口"
    echo "   - 如果使用云服务器，请在安全组中开放端口"
    echo "   - 首次访问可能需要等待几分钟"
}

# 主函数
main() {
    echo ""
    log_info "开始 DeerFlow Linux 一键部署..."
    echo ""
    
    # 检查系统
    detect_os
    check_root
    
    # 安装依赖
    install_docker
    install_docker_compose
    
    # 检查项目
    check_project_files
    
    # 配置环境
    setup_environment
    
    # 配置防火墙
    setup_firewall
    
    # 部署应用
    deploy_application
    
    # 显示部署信息
    show_deployment_info
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 