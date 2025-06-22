# 🚚 DeerFlow 项目迁移检查清单

这个检查清单帮助你将 DeerFlow 项目迁移到新的电脑上。

## 📦 迁移前准备

### 需要复制的文件和目录
- ✅ 整个项目文件夹
- ✅ `conf.yaml` 文件 (包含 LLM API 配置)
- ✅ `web/node_modules/` 目录 (前端依赖)
- ✅ `.env` 文件 (如果存在，包含搜索 API 配置)

### 不需要复制的文件
- ❌ `.venv/` 目录 (Python 虚拟环境，会重新创建)
- ❌ `outputs/` 目录 (输出文件，可选)
- ❌ `.next/` 目录 (前端构建缓存，会重新生成)

## 🖥️ 新电脑环境要求

### Docker 模式 (推荐)
```bash
# 只需要安装 Docker
docker --version
docker-compose --version
```

### 开发模式
```bash
# 需要安装以下工具
python --version  # 3.12+
uv --version       # Python 包管理器
node --version     # 22+
pnpm --version     # Node.js 包管理器
```

## 🚀 迁移步骤

### 方案 1: Docker 模式 (最简单)

1. **复制项目文件夹到新电脑**

2. **检查配置文件**
   ```bash
   # 确保 conf.yaml 存在且配置正确
   cat conf.yaml
   ```

3. **启动服务**
   ```bash
   cd deer-flow
   docker-compose up -d
   ```

4. **验证运行**
   ```bash
   # 前端: http://localhost:4051
   # 后端: http://localhost:8000
   curl http://localhost:4051
   curl http://localhost:8000/api/config
   ```

### 方案 2: 开发模式

1. **复制项目文件夹到新电脑**

2. **安装 Python 依赖**
   ```bash
   cd deer-flow
   uv sync
   ```

3. **检查前端依赖** (通常已包含在复制的文件中)
   ```bash
   cd web
   ls node_modules  # 应该存在
   # 如果不存在，运行: pnpm install
   ```

4. **启动服务**
   ```bash
   cd deer-flow
   ./bootstrap.sh -d
   ```

5. **验证运行**
   ```bash
   # 前端: http://localhost:9000
   # 后端: http://localhost:9001
   curl http://localhost:9000
   curl http://localhost:9001/api/config
   ```

## ⚙️ 配置检查

### 必需配置 (conf.yaml)
```yaml
BASIC_MODEL:
  base_url: https://openrouter.ai/api/v1
  model: "qwen/qwen3-235b-a22b"
  api_key: "sk-or-v1-your-api-key"  # ✅ 确保有效
```

### 可选配置 (.env)
```bash
# 搜索引擎 API (可选)
TAVILY_API_KEY=your_tavily_key
BRAVE_SEARCH_API_KEY=your_brave_key

# TTS 服务 (可选)
VOLCENGINE_TTS_API_KEY=your_tts_key
```

## 🔧 常见问题排除

### 端口冲突
```bash
# 检查端口占用
lsof -i :4051 -i :8000 -i :9000 -i :9001

# 停止冲突服务
docker-compose down
pkill -f "bootstrap.sh"
```

### 权限问题
```bash
# 确保脚本可执行
chmod +x bootstrap.sh
```

### 依赖问题
```bash
# 重新安装 Python 依赖
rm -rf .venv
uv sync

# 重新安装前端依赖 (如果需要)
cd web
rm -rf node_modules
pnpm install
```

## ✅ 验证清单

- [ ] 项目文件夹完整复制
- [ ] `conf.yaml` 配置正确
- [ ] 系统环境满足要求
- [ ] 服务启动成功
- [ ] 前端页面可访问
- [ ] 后端 API 响应正常
- [ ] 可以进行对话测试

## 🎯 快速验证脚本

创建一个快速验证脚本：

```bash
#!/bin/bash
echo "🔍 DeerFlow 迁移验证..."

# 检查文件
echo "📁 检查关键文件..."
[ -f "conf.yaml" ] && echo "✅ conf.yaml 存在" || echo "❌ conf.yaml 缺失"
[ -f "bootstrap.sh" ] && echo "✅ bootstrap.sh 存在" || echo "❌ bootstrap.sh 缺失"
[ -d "web/node_modules" ] && echo "✅ 前端依赖存在" || echo "⚠️ 前端依赖缺失"

# 检查环境
echo "🖥️ 检查系统环境..."
command -v docker >/dev/null 2>&1 && echo "✅ Docker 可用" || echo "⚠️ Docker 未安装"
command -v uv >/dev/null 2>&1 && echo "✅ uv 可用" || echo "⚠️ uv 未安装"
command -v pnpm >/dev/null 2>&1 && echo "✅ pnpm 可用" || echo "⚠️ pnpm 未安装"

echo "🎉 验证完成！"
```

## 📞 获取帮助

如果遇到问题：
1. 检查 `DEPLOYMENT_MODES.md` 文档
2. 查看项目的 `README.md`
3. 检查 Docker 容器日志: `docker-compose logs -f`
4. 检查开发模式日志输出 