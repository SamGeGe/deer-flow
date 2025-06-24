#!/bin/bash

# DeerFlow 通用部署脚本
# 支持 macOS 和 Windows (Git Bash/WSL)
# 适用于本地开发和小规模部署

set -e  # 遇到错误立即退出

echo "🦌 DeerFlow 通用部署脚本"
echo "========================"

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
    case "$(uname -s)" in
        Darwin)
            OS="macOS"
            VER=$(sw_vers -productVersion)
            ;;
        Linux)
            # 检查是否为WSL
            if grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
                OS="WSL"
                VER="Windows Subsystem for Linux"
            else
                OS="Linux"
                VER="Unknown"
                log_warning "检测到Linux系统，建议使用 deploy-linux.sh"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            OS="Windows"
            VER="Git Bash/MSYS"
            ;;
        *)
            log_error "不支持的系统类型: $(uname -s)"
            exit 1
            ;;
    esac
    log_info "检测到系统: $OS $VER"
}

# 检查Docker Desktop是否安装和运行
check_docker_desktop() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        case "$OS" in
            "macOS")
                log_info "请安装 Docker Desktop for Mac:"
                log_info "https://docs.docker.com/desktop/mac/"
                ;;
            "Windows"|"WSL")
                log_info "请安装 Docker Desktop for Windows:"
                log_info "https://docs.docker.com/desktop/windows/"
                ;;
        esac
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行"
        case "$OS" in
            "macOS")
                log_info "请启动 Docker Desktop 应用程序"
                ;;
            "Windows"|"WSL")
                log_info "请启动 Docker Desktop 应用程序"
                ;;
        esac
        exit 1
    fi
    
    log_success "Docker Desktop 已安装并运行"
}

# 检查Docker Compose
check_docker_compose() {
    if ! (command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1); then
        log_error "Docker Compose 未安装"
        case "$OS" in
            "macOS"|"Windows"|"WSL")
                log_info "Docker Compose 应该随 Docker Desktop 一起安装"
                log_info "请检查 Docker Desktop 是否正确安装"
                ;;
        esac
        exit 1
    fi
    log_success "Docker Compose 已安装"
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
        case "$OS" in
            "macOS"|"Linux"|"WSL")
                sed -i.bak 's|NEXT_PUBLIC_API_URL="http://localhost:8000/api"|NEXT_PUBLIC_API_URL="/api"|g' .env
                rm -f .env.bak
                ;;
            "Windows")
                sed -i 's|NEXT_PUBLIC_API_URL="http://localhost:8000/api"|NEXT_PUBLIC_API_URL="/api"|g' .env
                ;;
        esac
        
        log_success ".env 文件创建完成"
    else
        log_success ".env 文件已存在"
    fi
    
    # 检查配置文件
    if [ ! -f "conf.yaml" ]; then
        if [ -f "conf.yaml.example" ]; then
            log_warning "未找到 conf.yaml，请参考 conf.yaml.example 创建配置文件"
            log_info "或访问 docs/configuration_guide.md 查看配置指南"
        else
            log_error "未找到配置文件模板，请检查项目完整性"
            exit 1
        fi
    else
        log_success "配置文件检查完成"
    fi
}

# 部署应用
deploy_application() {
    log_info "开始部署应用..."
    
    # 停止可能存在的旧容器
    if docker compose ps -q &> /dev/null 2>&1; then
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

# 获取本机IP地址
get_local_ip() {
    case "$OS" in
        "macOS")
            LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
            ;;
        "WSL")
            # WSL需要获取Windows主机IP
            LOCAL_IP=$(ip route show | grep -i default | awk '{ print $3}')
            ;;
        "Windows")
            # Git Bash中获取IP
            LOCAL_IP=$(ipconfig | grep -A 1 "Wireless LAN adapter Wi-Fi" | grep "IPv4" | awk '{print $NF}' | tr -d '\r')
            if [ -z "$LOCAL_IP" ]; then
                LOCAL_IP=$(ipconfig | grep -A 1 "Ethernet adapter" | grep "IPv4" | awk '{print $NF}' | tr -d '\r')
            fi
            ;;
        *)
            LOCAL_IP="localhost"
            ;;
    esac
    
    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP="localhost"
    fi
}

# 显示部署信息
show_deployment_info() {
    get_local_ip
    
    echo ""
    echo "🎉 DeerFlow 部署完成！"
    echo "======================="
    echo ""
    echo "📱 访问地址："
    echo "   本地访问: http://localhost:4051"
    if [ "$LOCAL_IP" != "localhost" ]; then
        echo "   网络访问: http://$LOCAL_IP:4051"
    fi
    echo ""
    echo "🔧 管理命令："
    echo "   查看状态: docker compose ps"
    echo "   查看日志: docker compose logs -f"
    echo "   重启服务: docker compose restart"
    echo "   停止服务: docker compose down"
    echo ""
    echo "📚 配置说明："
    echo "   - 编辑 .env 文件配置环境变量"
    echo "   - 编辑 conf.yaml 文件配置模型"
    echo "   - 查看 docs/configuration_guide.md 获取详细配置指南"
    echo ""
    case "$OS" in
        "macOS")
            echo "💻 macOS 使用说明："
            echo "   - 服务运行在 Docker Desktop 中"
            echo "   - 可通过 Docker Desktop 界面管理容器"
            echo "   - 如需外网访问，请检查防火墙设置"
            ;;
        "Windows")
            echo "🪟 Windows 使用说明："
            echo "   - 服务运行在 Docker Desktop 中"
            echo "   - 可通过 Docker Desktop 界面管理容器"
            echo "   - 如需外网访问，请检查防火墙设置"
            ;;
        "WSL")
            echo "🐧 WSL 使用说明："
            echo "   - 服务运行在 WSL2 + Docker Desktop 中"
            echo "   - 可从 Windows 和 WSL 访问"
            echo "   - Windows 访问: http://localhost:4051"
            ;;
    esac
    echo ""
    echo "⚠️  注意事项："
    echo "   - 首次启动可能需要等待几分钟"
    echo "   - 确保 Docker Desktop 保持运行状态"
    echo "   - 如需使用搜索功能，请配置 Tavily API 密钥"
}

# 主函数
main() {
    echo ""
    log_info "开始 DeerFlow 通用部署..."
    echo ""
    
    # 检查系统
    detect_os
    
    # 检查依赖
    check_docker_desktop
    check_docker_compose
    
    # 检查项目
    check_project_files
    
    # 配置环境
    setup_environment
    
    # 部署应用
    deploy_application
    
    # 显示部署信息
    show_deployment_info
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 