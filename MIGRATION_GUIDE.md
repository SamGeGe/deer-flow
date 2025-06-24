# DeerFlow 项目移植指南

## 📦 基础移植步骤

### 1. 打包项目文件

```bash
# 使用 tar 打包（推荐）
tar -czf deer-flow.tar.gz \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.next' \
  --exclude='outputs' \
  deer-flow/
```

### 2. 传输到目标机器

```bash
# 通过 scp 传输到远程服务器
scp deer-flow.tar.gz username@server-ip:/path/to/destination/

# 或使用其他方式：rsync, 云存储, U盘等
```

### 3. 解压并进入目录

```bash
# 在目标机器上解压
tar -xzf deer-flow.tar.gz
cd deer-flow
```

## 🚀 根据目标平台选择部署方式

### 🐧 Linux 服务器部署（生产环境）

**适用于：** Ubuntu/Debian/CentOS/RHEL/Rocky/AlmaLinux 等 Linux 服务器

#### 系统要求
- 内存：建议 4GB+
- 存储：建议 10GB+ 可用空间
- 网络：需要访问外网（调用LLM API）

#### 一键部署
```bash
# 给脚本添加执行权限
chmod +x deploy-linux.sh

# 运行一键部署脚本
./deploy-linux.sh
```

**这是唯一需要的Linux生产部署脚本**，会自动：
- 安装 Docker 和 Docker Compose
- 配置防火墙开放 4051 端口
- 创建并配置 `.env` 文件
- 构建并启动所有服务容器

#### 外网访问
部署完成后可通过以下地址访问：
- 本地：`http://localhost:4051`
- 外网：`http://server-ip:4051`

### 💻 macOS 本地部署

**适用于：** macOS 开发机器或本地使用

#### 系统要求
- macOS 10.15+
- 需要安装 Docker Desktop for Mac

#### 一键部署
```bash
# 给脚本添加执行权限
chmod +x deploy-universal.sh

# 运行通用部署脚本
./deploy-universal.sh
```

脚本会自动：
- 检查 Docker Desktop 是否运行
- 创建并配置 `.env` 文件
- 构建并启动所有服务容器

#### 访问地址
- 本地：`http://localhost:4051`
- 网络：`http://你的Mac的IP:4051`

### 🪟 Windows 本地部署

**适用于：** Windows 开发机器或本地使用

#### 系统要求
- Windows 10/11
- 需要安装 Docker Desktop for Windows
- 需要 Git Bash 或 WSL2

#### 部署方式

**方式一：使用 Git Bash**
```bash
# 在 Git Bash 中运行
chmod +x deploy-universal.sh
./deploy-universal.sh
```

**方式二：使用 WSL2**
```bash
# 在 WSL2 中运行
chmod +x deploy-universal.sh
./deploy-universal.sh
```

#### 访问地址
- 本地：`http://localhost:4051`
- 网络：`http://你的Windows的IP:4051`

## 🖥️ 开发环境部署（所有平台）

### 开发模式特点
- 支持热重载
- 前后端分离运行
- 便于调试开发

### 环境要求
- Python 3.12+
- uv 0.7+
- Node.js 18+
- pnpm 8+

### 快速启动

```bash
# 1. 环境检查
./check-deployment.sh

# 2. 安装依赖
uv sync --locked
cd web && pnpm install && cd ..

# 3. 配置环境
cp env.example .env
# 编辑 .env 配置 API 密钥

# 4. 启动开发模式
./bootstrap.sh --dev
# 访问: http://localhost:9000
```

## ⚙️ 必需配置文件

### 1. conf.yaml - LLM模型配置
```yaml
BASIC_MODEL:
  model: "qwen/qwen3-235b-a22b"
  api_key: "your-openrouter-api-key"
  base_url: "https://openrouter.ai/api/v1"
```

### 2. .env - 环境变量配置
```bash
SEARCH_API=tavily
TAVILY_API_KEY=your-tavily-key
NEXT_PUBLIC_API_URL=/api  # 生产环境使用相对路径
```

**注意**: 
- `.env` 文件由部署脚本自动创建
- `conf.yaml` 需要手动配置
- Linux部署：`deploy-linux.sh` 自动创建 `.env`
- Windows/Mac部署：`deploy-universal.sh` 自动创建 `.env`

## 🔧 故障排除

### 通用问题

#### 1. API 认证失败
```bash
# 检查配置文件
cat conf.yaml
# 确保 OpenRouter API key 有效

# 测试 API 连接
curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen/qwen3-235b-a22b", "messages": [{"role": "user", "content": "test"}]}'
```

#### 2. 端口被占用
```bash
# 查看端口占用
# Linux/Mac/WSL
sudo lsof -i :4051

# Windows
netstat -ano | findstr :4051

# 修改端口（编辑 docker-compose.yml）
ports:
  - "4052:80"  # 改为其他端口
```

#### 3. 容器启动失败
```bash
# 查看详细错误日志
docker compose logs backend
docker compose logs frontend
docker compose logs nginx

# 重新构建容器
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 平台特定问题

#### Linux 服务器
```bash
# 检查防火墙状态
sudo ufw status
sudo firewall-cmd --list-ports

# 检查 nginx 配置
docker exec deer-flow-nginx nginx -t
```

#### macOS
```bash
# 检查 Docker Desktop 状态
docker info

# 检查本地防火墙
sudo pfctl -s all
```

#### Windows
```bash
# 检查 Docker Desktop 状态
docker info

# 检查防火墙
netsh advfirewall firewall show rule name="Docker Desktop"
```

## 📋 部署检查清单

### 部署前准备
- [ ] 确保有有效的 OpenRouter API key
- [ ] 检查系统要求（内存、存储、网络）
- [ ] 准备好 Tavily API key（搜索功能，可选）
- [ ] 确认端口 4051 可用且未被占用

### 平台特定准备
- [ ] **Linux**: 确保有 sudo 权限
- [ ] **macOS**: 安装并启动 Docker Desktop
- [ ] **Windows**: 安装 Docker Desktop + Git Bash 或 WSL2

### 部署执行
- [ ] **Linux**: 运行 `./deploy-linux.sh`
- [ ] **macOS/Windows**: 运行 `./deploy-universal.sh`
- [ ] 脚本执行完成无错误提示
- [ ] 所有Docker容器状态为 "Up"

### 部署验证
- [ ] 访问 `http://localhost:4051` 能正常打开界面
- [ ] 尝试发送测试消息，验证 LLM 响应正常
- [ ] 检查搜索功能是否正常工作
- [ ] 验证日志中无错误信息：`docker compose logs -f`

## 🚀 部署脚本对比

| 脚本 | 适用平台 | 功能 | 使用场景 |
|------|----------|------|----------|
| **`deploy-linux.sh`** | Linux 服务器 | 自动安装Docker、配置防火墙、生产部署 | 🎯 Linux 生产服务器 |
| **`deploy-universal.sh`** | macOS、Windows | 检查Docker Desktop、本地部署 | 💻 本地开发和测试 |
| **`bootstrap.sh`** | 所有平台 | 开发模式启动 | 🔧 开发调试 |

### 选择指南
- **Linux 服务器生产部署** → 使用 `deploy-linux.sh`
- **macOS 本地使用** → 使用 `deploy-universal.sh`
- **Windows 本地使用** → 使用 `deploy-universal.sh`
- **开发调试** → 使用 `bootstrap.sh --dev`

## 📱 访问地址总结

| 部署方式 | 本地访问 | 外网访问 | 说明 |
|----------|----------|----------|------|
| Linux 生产 | http://localhost:4051 | http://server-ip:4051 | 需要防火墙开放端口 |
| macOS 本地 | http://localhost:4051 | http://mac-ip:4051 | 需要防火墙允许 |
| Windows 本地 | http://localhost:4051 | http://windows-ip:4051 | 需要防火墙允许 |
| 开发模式 | http://localhost:9000 | - | 仅本地开发 |

---

**📞 获取帮助**

如果遇到问题：
1. 查看 `docker compose logs -f` 获取详细错误信息
2. 检查 `docs/FAQ.md` 常见问题解答
3. 运行 `./check-deployment.sh` 进行环境检查
4. 在 GitHub Issues 中寻找解决方案

**💡 关键提示**:
- **Linux 服务器**: 使用 `./deploy-linux.sh` 一键部署
- **macOS/Windows**: 使用 `./deploy-universal.sh` 一键部署
- **开发调试**: 使用 `./bootstrap.sh --dev` 开发模式 