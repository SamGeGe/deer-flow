# 🐧 DeerFlow Linux 一键部署指南

快速在Linux服务器上部署DeerFlow深度研究框架。

## 🚀 一键部署

```bash
# 运行一键部署脚本
./deploy-linux.sh
```

## 📋 支持的系统

- ✅ Ubuntu 18.04+
- ✅ Debian 10+
- ✅ CentOS 7+
- ✅ RHEL 7+
- ✅ Rocky Linux
- ✅ AlmaLinux

## 🔧 系统要求

- **内存**：最少 2GB，推荐 4GB+
- **存储**：最少 5GB 可用空间
- **网络**：需要访问 Docker Hub 和 GitHub
- **权限**：需要 sudo 权限安装依赖

## 📱 部署后访问

- **前端界面**：`http://服务器IP:4051`
- **本地访问**：`http://localhost:4051`

## 🛠️ 管理命令

```bash
# 查看服务状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 更新服务
docker compose pull && docker compose up -d
```

## ⚙️ 配置文件

### 环境变量配置 (.env)
```bash
# 编辑环境变量
nano .env

# 主要配置项：
SEARCH_API=bocha                     # 搜索引擎
BOCHA_API_KEY=sk-your-api-key       # 博查AI API密钥（推荐）
TAVILY_API_KEY=tvly-your-api-key    # Tavily API密钥（可选）
NEXT_PUBLIC_API_URL=/api            # API路径（相对路径）
```

更多配置说明请参考：[配置指南](docs/configuration_guide.md)

## 🔍 搜索引擎配置

### 使用博查AI（推荐中文搜索）
```bash
# 设置博查AI API密钥
./set-bocha-key.sh sk-your-bocha-api-key

# 或手动编辑.env
SEARCH_API=bocha
BOCHA_API_KEY=sk-your-api-key
```

### 使用Tavily（推荐英文搜索）
```bash
# 设置Tavily API密钥
./set-tavily-key.sh tvly-your-tavily-api-key

# 或手动编辑.env
SEARCH_API=tavily
TAVILY_API_KEY=tvly-your-api-key
```

### 使用DuckDuckGo（免费，无需API密钥）
```bash
# .env文件中设置
SEARCH_API=duckduckgo
```

## 🔒 安全配置

### 防火墙设置
脚本会自动配置防火墙，手动配置方法：

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 4051/tcp

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=4051/tcp
sudo firewall-cmd --reload
```

### 云服务器安全组
如果使用云服务器，请在安全组中开放：
- **入站规则**：TCP 4051 端口
- **来源**：0.0.0.0/0 (或指定IP范围)

## 🐳 Docker配置说明

### 服务架构
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Nginx (80)    │───▶│  Frontend (3000) │    │  Backend (8000) │
│  反向代理        │    │     前端服务      │◀───│    后端服务      │
│  Port: 4051     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 端口映射
- **外部访问**：4051 → Nginx (80)
- **内部通信**：
  - Nginx → Frontend (3000)
  - Nginx → Backend (8000)

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :4051
   
   # 停止占用进程
   sudo kill -9 <PID>
   ```

2. **Docker权限问题**
   ```bash
   # 添加用户到docker组
   sudo usermod -aG docker $USER
   
   # 重新登录或运行
   newgrp docker
   ```

3. **服务启动失败**
   ```bash
   # 查看详细日志
   docker compose logs
   
   # 重新构建
   docker compose build --no-cache
   docker compose up -d
   ```

4. **网络连接问题**
   ```bash
   # 检查容器网络
   docker network ls
   docker network inspect deer-flow_deer-flow-network
   ```

### 日志查看

```bash
# 查看所有服务日志
docker compose logs

# 查看特定服务日志
docker compose logs backend
docker compose logs frontend
docker compose logs nginx

# 实时跟踪日志
docker compose logs -f --tail=100
```

### 性能优化

```bash
# 清理无用的Docker资源
docker system prune -f

# 查看资源使用情况
docker stats

# 限制容器资源（可选）
# 编辑 docker-compose.yml 添加资源限制
```

## 📚 更多文档

- [完整部署模式说明](DEPLOYMENT_MODES.md)
- [配置指南](docs/configuration_guide.md)
- [FAQ常见问题](docs/FAQ.md)

## 🆘 获取帮助

如果遇到问题：

1. 查看 [FAQ文档](docs/FAQ.md)
2. 检查 [GitHub Issues](https://github.com/bytedance/deer-flow/issues)
3. 查看详细日志：`docker compose logs -f`

---

**部署成功后，访问 `http://服务器IP:4051` 开始使用DeerFlow！** 🎉 