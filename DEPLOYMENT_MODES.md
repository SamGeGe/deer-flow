# DeerFlow 部署模式说明

DeerFlow 支持多种部署模式，适用于不同的使用场景和操作系统。

## 🐧 Linux 一键部署 (推荐)

适用于 Linux 服务器快速部署，支持 Ubuntu/Debian/CentOS/RHEL 等主流发行版。

### 快速开始

```bash
# 1. 复制项目到Linux服务器
scp -r deer-flow/ user@your-server:/path/to/destination/

# 2. 登录服务器并进入项目目录
ssh user@your-server
cd /path/to/destination/deer-flow

# 3. 运行一键部署脚本
./deploy-linux.sh
```

### 部署特性

- ✅ **自动检测系统**：支持 Ubuntu/Debian/CentOS/RHEL
- ✅ **自动安装依赖**：Docker、Docker Compose
- ✅ **智能配置**：自动创建 .env 文件和配置
- ✅ **防火墙配置**：自动开放必要端口
- ✅ **服务监控**：检查部署状态和服务健康
- ✅ **Nginx反向代理**：统一入口，IP变化无需修改配置

### 访问地址

- **前端界面**：`http://服务器IP:4051`
- **管理命令**：
  ```bash
  docker compose ps          # 查看状态
  docker compose logs -f     # 查看日志
  docker compose restart     # 重启服务
  docker compose down        # 停止服务
  ```

### 系统要求

- **操作系统**：Ubuntu 18.04+, Debian 10+, CentOS 7+, RHEL 7+
- **内存**：最少 2GB，推荐 4GB+
- **存储**：最少 5GB 可用空间
- **网络**：需要访问 Docker Hub 和 GitHub

---

## 💻 本地部署模式

DeerFlow 支持两种独立的本地部署模式，每种模式使用不同的端口和配置，可以独立使用而不互相冲突。

## 🚀 模式对比

| 特性 | 开发模式 | Docker 模式 |
|------|----------|-------------|
| 启动命令 | `./bootstrap.sh -d` | `docker-compose up -d` |
| 前端端口 | 9000 | 4051 |
| 后端端口 | 9001 | 8000 |
| 前端访问 | http://localhost:9000 | http://localhost:4051 |
| 后端 API | http://localhost:9001 | http://localhost:8000 |
| API 文档 | http://localhost:9001/docs | http://localhost:8000/docs |
| 热重载 | ✅ 支持 | ❌ 不支持 |
| 容器化 | ❌ 本地运行 | ✅ Docker 容器 |
| 搜索引擎 | 博查AI → DuckDuckGo | 博查AI → DuckDuckGo |
| 适用场景 | 开发调试 | 生产部署 |

## 🔍 搜索引擎配置

DeerFlow 支持多种搜索引擎，智能回退机制：

1. **博查AI** (推荐中文搜索)
   - 专为中文优化，1秒响应时间
   - 高质量中文内容，数据合规不出海
   - 获取地址: https://www.bochaai.com/

2. **Tavily** (推荐英文搜索)
   - 专为AI应用优化的搜索API
   - 获取地址: https://app.tavily.com/

3. **DuckDuckGo** (免费备选)
   - 当付费搜索引擎不可用时自动切换
   - 无需API密钥，开箱即用

### 设置博查AI API 密钥

**方法一：使用脚本设置**

```bash
# 快速设置脚本
./set-bocha-key.sh sk-your-bocha-api-key
```

**方法二：手动设置环境变量**

```bash
# 临时设置 (当前会话)
export BOCHA_API_KEY=sk-your-bocha-api-key
```

**方法三：编辑.env文件**

```bash
echo "BOCHA_API_KEY=sk-your-bocha-api-key" >> .env
```

### 设置 Tavily API 密钥

**使用脚本设置**

```bash
# 快速设置脚本
./set-tavily-key.sh tvly-your-tavily-api-key
```

## 📋 使用方法

### 开发模式 (推荐用于开发)

```bash
# 启动开发模式
./bootstrap.sh -d

# 访问地址
# 前端: http://localhost:9000
# 后端: http://localhost:9001/docs (API 文档)
```

**特点:**
- 自动创建 `.env` 文件（开发模式专用）
- 支持热重载，代码修改后自动重启
- 前后端分离运行，便于调试
- 按 `Ctrl+C` 停止所有服务
- 自动检测 Tavily API 密钥，无密钥时回退到 DuckDuckGo

### Docker 模式 (推荐用于生产)

```bash
# 启动 Docker 模式
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 访问地址
# 前端: http://localhost:4051
# 后端: http://localhost:8000/docs (API 文档)
```

**特点:**
- 完全容器化，环境一致性好
- 自动构建和部署
- 支持生产环境使用
- 自动读取宿主机的 `TAVILY_API_KEY` 环境变量

## 🛠️ 故障排除

### 搜索功能问题

1. **检查搜索引擎状态**

   ```bash
   # 查看当前搜索引擎配置
   grep SEARCH_API .env
   
   # 查看API密钥状态
   grep BOCHA_API_KEY .env
   grep TAVILY_API_KEY .env
   ```

2. **API 密钥问题**

   ```bash
   # 检查博查AI密钥
   echo $BOCHA_API_KEY
   
   # 检查Tavily密钥
   echo $TAVILY_API_KEY
   
   # 或检查.env文件
   grep BOCHA_API_KEY .env
   grep TAVILY_API_KEY .env
   ```

3. **搜索引擎回退机制**
   - 系统会自动从博查AI或Tavily回退到 DuckDuckGo
   - 如果搜索功能异常，请检查网络连接

### 端口冲突

如果遇到端口被占用：

```bash
# 检查端口占用
lsof -i :4051  # Docker 前端
lsof -i :8000  # Docker 后端
lsof -i :9000  # 开发前端
lsof -i :9001  # 开发后端

# 停止占用进程
kill -9 <PID>
```

### 容器问题

```bash
# 重新构建容器
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 清理无用容器和镜像
docker system prune -f
```

## 🔧 高级配置

### 自定义搜索引擎

可以通过环境变量自定义搜索引擎：

```bash
# 搜索引擎选择
SEARCH_API=bocha          # 推荐中文搜索，博查AI
# SEARCH_API=tavily       # 推荐英文搜索，Tavily
# SEARCH_API=duckduckgo   # 仅使用 DuckDuckGo
# SEARCH_API=brave_search # 使用 Brave 搜索 (需要 API 密钥)
# SEARCH_API=arxiv        # 仅搜索学术论文

# API 密钥配置
BOCHA_API_KEY=sk-your-bocha-key
TAVILY_API_KEY=tvly-your-tavily-key
BRAVE_SEARCH_API_KEY=your-brave-key
```

### 环境变量优先级

1. 命令行环境变量 (最高优先级)
2. `.env` 文件
3. 系统默认值 (最低优先级)

### 开发调试

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 启动开发模式
./bootstrap.sh -d
```

## 📚 相关文档

- [配置指南](docs/configuration_guide.md)
- [项目迁移检查清单](MIGRATION_CHECKLIST.md)
- [修复总结](FIXES_SUMMARY.md)

## 🔄 最新更新

**v2.0 更新内容**：
- ✅ 修复了 Docker 模式下的搜索 API 错误
- ✅ 添加了 favicon.ico 支持
- ✅ 改进了开发模式的启动脚本
- ✅ 默认使用 DuckDuckGo 搜索引擎
- ✅ 优化了错误处理和日志输出
- ✅ 完善了两种模式的独立性 