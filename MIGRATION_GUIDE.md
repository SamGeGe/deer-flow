# DeerFlow 项目移植指南

## 📦 将项目复制到其他电脑

### 1. 打包项目

在当前电脑上，打包项目文件：

```bash
# 方法一：使用 tar 打包
tar -czf deer-flow.tar.gz \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.next' \
  --exclude='outputs' \
  deer-flow/

# 方法二：使用 zip 打包
zip -r deer-flow.zip deer-flow/ \
  -x "deer-flow/.git/*" \
  -x "deer-flow/node_modules/*" \
  -x "deer-flow/.venv/*" \
  -x "deer-flow/__pycache__/*" \
  -x "deer-flow/.next/*" \
  -x "deer-flow/outputs/*"
```

### 2. 传输到新电脑

将打包文件传输到新电脑：

- **网络传输**: scp, rsync, 云存储等
- **物理媒体**: U盘, 移动硬盘等
- **代码仓库**: Git clone (如果已推送到仓库)

### 3. 在新电脑上解压

```bash
# 解压 tar.gz
tar -xzf deer-flow.tar.gz

# 解压 zip
unzip deer-flow.zip

# 进入项目目录
cd deer-flow
```

### 4. 环境准备

#### 4.1 安装系统依赖

参考 `QUICK_START.md` 安装必需的工具：
- Python 3.12+
- uv 0.7+
- Node.js 18+
- pnpm 8+

#### 4.2 运行环境检查

```bash
# 给脚本添加执行权限
chmod +x check-deployment.sh
chmod +x bootstrap.sh
chmod +x set-tavily-key.sh

# 运行环境检查
./check-deployment.sh
```

### 5. 安装依赖

#### 5.1 Python 依赖

```bash
# 安装 Python 依赖
uv sync --locked
```

#### 5.2 前端依赖

```bash
# 安装前端依赖
cd web
pnpm install
cd ..
```

### 6. 配置环境

#### 6.1 创建环境配置

```bash
# 复制环境配置模板
cp env.example .env
```

#### 6.2 配置 API 密钥

```bash
# 设置 Tavily API 密钥 (可选但推荐)
./set-tavily-key.sh your_tavily_api_key

# 或者手动编辑 .env 文件
nano .env  # 或使用其他编辑器
```

### 7. 启动服务

#### 7.1 开发模式

```bash
# 启动开发模式
./bootstrap.sh --dev

# 访问地址
# 前端: http://localhost:9000
# 后端: http://localhost:9001
```

#### 7.2 Docker 模式

```bash
# 启动 Docker 服务
docker-compose up -d

# 访问地址
# 前端: http://localhost:4051
# 后端: http://localhost:8000
```

### 8. 验证功能

1. 访问前端页面
2. 尝试发起一个研究任务
3. 检查搜索和 LLM 调用是否正常

### 9. 故障排除

#### 9.1 依赖问题

```bash
# 重新安装 Python 依赖
rm -rf .venv
uv sync --locked

# 重新安装前端依赖
cd web
rm -rf node_modules
pnpm install
cd ..
```

#### 9.2 端口冲突

检查并修改配置中的端口：
- 开发模式：修改 `bootstrap.sh` 中的端口
- Docker 模式：修改 `docker-compose.yml` 中的端口映射

#### 9.3 权限问题

```bash
# 确保脚本有执行权限
chmod +x *.sh
```

### 10. 配置持久化

#### 10.1 保存自定义配置

如果你修改了配置，记得备份：
- `.env` - 环境变量配置
- `conf.yaml` - 模型配置
- `docker-compose.yml` - Docker 配置 (如果有修改)

#### 10.2 版本控制

建议将项目纳入版本控制：

```bash
# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库 (可选)
git remote add origin your-repo-url
git push -u origin main
```

### 11. 自动化脚本

创建一键部署脚本 `deploy.sh`：

```bash
#!/bin/bash
echo "🚀 DeerFlow 一键部署"

# 检查环境
./check-deployment.sh

# 安装依赖
echo "安装 Python 依赖..."
uv sync --locked

echo "安装前端依赖..."
cd web && pnpm install && cd ..

# 配置环境
if [ ! -f .env ]; then
    cp env.example .env
    echo "已创建 .env 文件，请配置 API 密钥"
fi

echo "✅ 部署完成！"
echo "运行 './bootstrap.sh --dev' 启动开发模式"
echo "或运行 'docker-compose up -d' 启动 Docker 模式"
```

### 12. 注意事项

- **不要复制** `.git`, `node_modules`, `.venv` 等目录
- **确保** API 密钥在新环境中重新配置
- **检查** 防火墙设置，确保端口可访问
- **验证** 网络连接，确保可以访问外部 API

这样就能确保项目在任何新电脑上都能正常运行！ 