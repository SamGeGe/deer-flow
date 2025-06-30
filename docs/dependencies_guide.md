# DeerFlow 依赖管理指南

## 📋 依赖文件概览

DeerFlow 项目的依赖信息分布在以下文件中：

```
deer-flow/
├── pyproject.toml          # 后端Python依赖配置
├── uv.lock                # 后端依赖版本锁定文件
├── web/
│   ├── package.json       # 前端Node.js依赖配置  
│   └── pnpm-lock.yaml     # 前端依赖版本锁定文件
└── deploy-linux.sh        # 系统依赖安装脚本
```

## 🐍 后端Python依赖

### 主要配置文件：`pyproject.toml`

**核心依赖类别：**

#### AI/ML框架
- `langchain-community` - LangChain社区组件
- `langchain-openai` - OpenAI集成
- `langgraph` - AI工作流图框架
- `litellm` - 统一LLM API接口
- `langchain-deepseek` - 深度求索集成
- `langchain-mcp-adapters` - MCP协议适配器

#### Web框架
- `fastapi` - 现代Web API框架
- `uvicorn` - ASGI服务器
- `sse-starlette` - 服务器发送事件支持

#### 搜索与爬虫
- `duckduckgo-search` - DuckDuckGo搜索
- `arxiv` - 学术论文搜索
- `readabilipy` - 网页内容提取
- `httpx` - 现代HTTP客户端

#### 数据处理
- `pandas` - 数据分析
- `numpy` - 数值计算
- `matplotlib` - 图表绘制
- `json-repair` - JSON修复

#### 其他工具
- `python-dotenv` - 环境变量管理
- `jinja2` - 模板引擎
- `inquirerpy` - 交互式命令行

### 依赖管理命令

```bash
# 安装所有依赖（自动创建虚拟环境）
uv sync

# 安装锁定版本的依赖
uv sync --locked

# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 更新依赖
uv lock --upgrade

# 查看已安装的包
uv pip list

# 检查依赖冲突
uv pip check
```

## 🌐 前端React/Next.js依赖

### 主要配置文件：`web/package.json`

**核心依赖类别：**

#### 框架与构建
- `next` - React全栈框架
- `react` & `react-dom` - React核心
- `typescript` - TypeScript支持

#### UI组件库
- `@radix-ui/*` - 无头UI组件集合
- `lucide-react` - 图标库
- `framer-motion` - 动画库
- `@tailwindcss/*` - CSS框架

#### 编辑器
- `@tiptap/*` - 富文本编辑器
- `novel` - AI增强编辑器
- `highlight.js` - 代码高亮

#### 可视化
- `@xyflow/react` - 流程图组件
- `mermaid` - 图表渲染
- `katex` - 数学公式渲染

#### 状态管理
- `zustand` - 轻量状态管理
- `immer` - 不可变状态

#### 文档导出
- `jspdf` - PDF生成
- `html2canvas` - HTML转图片
- `docx` - Word文档生成
- `file-saver` - 文件下载

### 依赖管理命令

```bash
cd web

# 安装所有依赖
pnpm install

# 安装锁定版本的依赖
pnpm install --frozen-lockfile

# 添加新依赖
pnpm add package-name

# 添加开发依赖
pnpm add -D package-name

# 更新依赖
pnpm update

# 查看过时的包
pnpm outdated

# 查看依赖树
pnpm list --depth=1
```

## 🐳 系统依赖

### Docker部署（推荐）

**自动安装系统依赖：**

```bash
# 运行部署脚本，自动安装Docker和Docker Compose
./deploy-linux.sh
```

**手动安装系统依赖：**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# CentOS/RHEL
sudo yum install -y docker docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 本地开发环境

**必需工具：**

- **Python 3.12+** - 后端运行环境
- **Node.js 18+** - 前端运行环境
- **uv 0.7+** - Python包管理器
- **pnpm 8+** - 前端包管理器

**安装脚本：**

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 pnpm (需要先安装Node.js)
npm install -g pnpm
```

## 🔧 依赖故障排除

### 常见问题

#### 1. Python依赖安装失败

```bash
# 清理缓存重新安装
uv cache clean
uv sync --reinstall

# 指定Python版本
uv python install 3.12
uv sync
```

#### 2. 前端依赖安装失败

```bash
cd web

# 清理缓存
pnpm store prune
rm -rf node_modules pnpm-lock.yaml

# 重新安装
pnpm install
```

#### 3. Docker构建失败

```bash
# 清理Docker缓存
docker system prune -f

# 重新构建无缓存
docker-compose build --no-cache
```

#### 4. 权限问题

```bash
# 添加用户到docker组
sudo usermod -aG docker $USER

# 重新登录生效
newgrp docker
```

### 依赖版本冲突

**检查冲突：**

```bash
# Python依赖冲突
uv pip check

# 前端依赖冲突  
cd web && pnpm audit
```

**解决方案：**

1. **锁定版本** - 使用 `uv.lock` 和 `pnpm-lock.yaml`
2. **清理重装** - 删除虚拟环境和node_modules重新安装
3. **版本降级** - 降级冲突的包到兼容版本

## 📊 依赖大小优化

### 生产环境优化

```bash
# 仅安装生产依赖
uv sync --no-dev

# 前端构建优化
cd web && pnpm build
```

### 清理开发文件

参考 [`CLEANUP_GUIDE.md`](../CLEANUP_GUIDE.md) 进行项目大小优化

## 🚀 依赖更新策略

### 定期更新

```bash
# 检查过时的包
uv lock --upgrade-package package-name
cd web && pnpm outdated

# 安全更新
cd web && pnpm audit fix
```

### 版本策略

- **主版本** - 谨慎更新，需要充分测试
- **次版本** - 定期更新，注意兼容性
- **补丁版本** - 及时更新，修复安全问题

## 📚 相关文档

- [QUICK_START.md](../QUICK_START.md) - 快速开始指南
- [DEPLOYMENT_MODES.md](../DEPLOYMENT_MODES.md) - 部署模式详解
- [CLEANUP_GUIDE.md](../CLEANUP_GUIDE.md) - 项目清理指南 