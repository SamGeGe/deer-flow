# DeerFlow 快速开始指南

## 🚀 在新电脑上部署 DeerFlow

### 1. 系统要求

**必需：**
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 0.7+ (Python 包管理器)
- Node.js 18+
- [pnpm](https://pnpm.io/) 8+ (前端包管理器)

**可选 (Docker 模式)：**
- Docker
- Docker Compose

### 2. 安装依赖工具

#### macOS
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Node.js (使用 Homebrew)
brew install node

# 安装 pnpm
npm install -g pnpm
```

#### Linux
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 pnpm
npm install -g pnpm
```

#### Windows
```powershell
# 安装 uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 安装 Node.js (从官网下载安装包)
# https://nodejs.org/

# 安装 pnpm
npm install -g pnpm
```

### 3. 部署检查

运行部署检查脚本，确保环境配置正确：

```bash
chmod +x check-deployment.sh
./check-deployment.sh
```

### 4. 启动方式

#### 方式一：开发模式 (推荐用于开发和测试)

```bash
# 启动开发模式
./bootstrap.sh --dev

# 访问地址
# 前端: http://localhost:9000
# 后端: http://localhost:9001
# API 文档: http://localhost:9001/docs
```

#### 方式二：Docker 模式 (推荐用于生产环境)

```bash
# 启动 Docker 服务
docker-compose up -d

# 访问地址
# 前端: http://localhost:4051
# 后端: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 5. 配置 API 密钥

#### 博查AI搜索 (推荐中文搜索)

```bash
# 设置博查AI API 密钥
./set-bocha-key.sh sk-your-bocha-api-key

# 或者手动编辑 .env 文件
cp env.example .env
# 编辑 .env 文件，设置 BOCHA_API_KEY=sk-your-api-key
```

#### 获取博查AI API 密钥

1. 访问 [博查AI](https://www.bochaai.com/)
2. 注册账户并获取 API 密钥
3. 专为中文优化，1秒响应，高质量中文内容

#### Tavily 搜索 API (推荐英文搜索)

```bash
# 设置 Tavily API 密钥
./set-tavily-key.sh tvly-your-tavily-api-key

# 或者手动编辑 .env 文件
cp env.example .env
# 编辑 .env 文件，设置 TAVILY_API_KEY=tvly-your-api-key
```

#### 搜索引擎选择

在 `.env` 文件中设置 `SEARCH_API` 变量：

```bash
# 选择搜索引擎：bocha, tavily, duckduckgo, brave_search, arxiv
SEARCH_API=bocha          # 推荐中文搜索
# 或者
SEARCH_API=tavily         # 推荐英文搜索
```

### 6. 配置 LLM 模型

DeerFlow 需要配置 LLM 模型才能正常工作。编辑 `conf.yaml` 文件：

```bash
# 编辑模型配置文件
nano conf.yaml
```

#### 支持的模型类型

- **OpenAI 模型**: GPT-4o, GPT-4 等
- **国产模型**: 豆包、通义千问、深度求索等
- **本地模型**: Ollama 支持的模型
- **云服务模型**: Azure OpenAI、OpenRouter 等

#### 配置示例

```yaml
# 基础模型配置
BASIC_MODEL:
  model: "gpt-4o"
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "https://api.openai.com/v1"

# 推理模型配置 (可选)
REASONING_MODEL:
  model: "deepseek-reasoner"
  api_key: "YOUR_DEEPSEEK_API_KEY"
  base_url: "https://api.deepseek.com"

# 视觉模型配置 (可选)
VISION_MODEL:
  model: "gpt-4o"
  api_key: "YOUR_OPENAI_API_KEY"
  base_url: "https://api.openai.com/v1"
```

#### 获取 API 密钥

1. **OpenAI**: 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. **深度求索**: 访问 [DeepSeek](https://platform.deepseek.com/api-keys)
3. **通义千问**: 访问 [阿里云百炼](https://bailian.console.aliyun.com/)
4. **豆包**: 访问 [火山引擎](https://console.volcengine.com/ark)

更多配置选项请参考 [配置指南](docs/configuration_guide.md)

### 7. 常见问题

#### 端口冲突
如果遇到端口冲突，请确保以下端口未被占用：
- 开发模式：9000 (前端), 9001 (后端)
- Docker 模式：4051 (前端), 8000 (后端)

#### 依赖安装失败
```bash
# 重新安装 Python 依赖
uv sync --locked

# 重新安装前端依赖
cd web && pnpm install
```

**详细的依赖管理说明请参考：[依赖管理指南](docs/dependencies_guide.md)**

#### 搜索功能不工作
- 确保已配置博查AI或Tavily API 密钥
- 博查AI：`./set-bocha-key.sh sk-your-api-key`
- Tavily：`./set-tavily-key.sh tvly-your-api-key`
- 或者依赖 DuckDuckGo 作为免费搜索引擎

### 8. 项目结构

```
deer-flow/
├── src/                    # 后端源码
├── web/                    # 前端源码
├── conf.yaml              # 模型配置
├── env.example            # 环境变量模板
├── bootstrap.sh           # 开发模式启动脚本
├── docker-compose.yml     # Docker 配置
├── check-deployment.sh    # 部署检查脚本
├── set-bocha-key.sh       # 博查AI密钥设置脚本
└── set-tavily-key.sh      # Tavily密钥设置脚本
```

### 9. 下一步

- 查看 `docs/` 目录了解更多配置选项
- 参考 `examples/` 目录查看使用示例
- 阅读 `CONTRIBUTING` 了解如何贡献代码

### 10. 获取帮助

如果遇到问题：
1. 运行 `./check-deployment.sh` 检查环境
2. 查看 `docs/FAQ.md` 常见问题
3. 检查 GitHub Issues
4. 提交新的 Issue 描述问题 