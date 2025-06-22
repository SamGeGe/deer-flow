# DeerFlow 部署模式说明

DeerFlow 支持两种独立的部署模式，每种模式使用不同的端口和配置，可以独立使用而不互相冲突。

## 🚀 模式对比

| 特性 | 开发模式 | Docker 模式 |
|------|----------|-------------|
| 启动命令 | `./bootstrap.sh -d` | `docker-compose up -d` |
| 前端端口 | 9000 | 4051 |
| 后端端口 | 9001 | 8000 |
| 前端访问 | http://localhost:9000 | http://localhost:4051 |
| 后端 API | http://localhost:9001 | http://localhost:8000 |
| 热重载 | ✅ 支持 | ❌ 不支持 |
| 容器化 | ❌ 本地运行 | ✅ Docker 容器 |
| 适用场景 | 开发调试 | 生产部署 |

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
- 完全容器化，环境隔离
- 生产级配置
- 自动重启策略
- 独立的网络和存储

## ⚙️ 配置说明

### 环境变量配置

两种模式使用不同的环境变量配置：

- **开发模式**: 自动生成 `.env` 文件，无需手动配置
- **Docker 模式**: 在 `docker-compose.yml` 中直接配置，不依赖 `.env` 文件

### 自定义配置 (可选)

如果需要自定义配置，可以：

1. 复制模板文件：
   ```bash
   cp env.template .env
   ```

2. 根据使用模式编辑 `.env` 文件：
   ```bash
   # 开发模式配置
   NEXT_PUBLIC_API_URL=http://localhost:9001
   NODE_ENV=development
   
   # 或 Docker 模式配置
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NODE_ENV=production
   ```

## 🔧 故障排除

### 端口冲突

如果遇到端口冲突，检查是否同时运行了两种模式：

```bash
# 检查端口占用
lsof -i :9000 -i :9001 -i :4051 -i :8000

# 停止开发模式
pkill -f "bootstrap.sh"

# 停止 Docker 模式
docker-compose down
```

### 环境变量问题

1. **开发模式**: 删除 `.env` 文件，重新启动会自动生成
2. **Docker 模式**: 检查 `docker-compose.yml` 中的环境变量配置

### 网络连接问题

- **开发模式**: 确保前端使用 `http://localhost:9001` 访问后端
- **Docker 模式**: 确保前端使用 `http://localhost:8000` 访问后端

## 📝 最佳实践

1. **开发时使用开发模式**：支持热重载，调试方便
2. **部署时使用 Docker 模式**：环境一致，便于管理  
3. **不要同时运行两种模式**：避免端口冲突和配置混乱
4. **定期清理**：停止不使用的服务释放资源

## 🆘 获取帮助

如果遇到问题，请检查：
1. 端口是否被占用
2. 环境变量配置是否正确
3. Docker 服务是否正常运行
4. 查看相应的日志输出 