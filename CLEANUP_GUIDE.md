# DeerFlow 项目清理指南

## 📊 项目大小优化

DeerFlow 项目包含完整的开发环境和依赖，原始大小约为 **973M**。本指南提供了多种清理选项来减少项目大小，同时保持项目功能完整。

## 🧹 清理选项

### 1. 基础清理（推荐）

**脚本：** `./cleanup.sh`  
**减少大小：** ~88M (973M → 885M)  
**影响：** 无，项目立即可用

**清理内容：**
- ✅ Python 缓存文件 (`__pycache__`, `*.pyc`)
- ✅ 系统缓存文件 (`.DS_Store`, `Thumbs.db`)
- ✅ 前端构建缓存 (`.next`)
- ✅ 临时文件 (`*.tmp`, `*.log`, `*.bak`)
- ✅ 输出目录内容
- ✅ 多余的文档文件
- ✅ IDE 和编辑器文件

```bash
# 运行基础清理
./cleanup.sh
```

### 2. 激进清理（最大化减少大小）

**脚本：** `./cleanup-aggressive.sh`  
**减少大小：** ~850M+ (973M → ~120M)  
**影响：** 需要重新安装依赖才能运行

**额外清理内容：**
- 🔥 前端依赖 (`web/node_modules` - 629M)
- 🔥 Python 虚拟环境 (`.venv`)
- 🔥 示例文件 (`examples/` - 92K)
- 🔥 测试文件 (`tests/` - 260K，可选)
- 🔥 资源文件 (`assets/` - 152K，可选)
- 🔥 锁文件 (`uv.lock`, `pnpm-lock.yaml`，可选)

```bash
# 运行激进清理（交互式）
./cleanup-aggressive.sh
```

## 📋 大小对比

| 清理级别 | 项目大小 | 节省空间 | 可立即运行 |
|---------|---------|---------|-----------|
| 原始项目 | 973M | - | ✅ |
| 基础清理 | 885M | 88M | ✅ |
| 激进清理 | ~120M | ~850M | ❌ (需重装依赖) |

## 🔧 恢复项目运行

### 激进清理后的恢复步骤：

1. **安装 Python 依赖：**
   ```bash
   uv sync
   ```

2. **安装前端依赖：**
   ```bash
   cd web && pnpm install
   ```

3. **验证环境：**
   ```bash
   ./check-deployment.sh
   ```

4. **启动项目：**
   ```bash
   # 开发模式
   ./bootstrap.sh --dev
   
   # 或 Docker 模式
   docker-compose up -d
   ```

## 💡 使用建议

### 日常开发
- 使用 **基础清理** (`./cleanup.sh`)
- 定期清理缓存和临时文件
- 保持依赖完整，项目随时可用

### 项目分发/备份
- 使用 **激进清理** (`./cleanup-aggressive.sh`)
- 大幅减少文件大小
- 接收方需要重新安装依赖

### 版本控制
如果使用 Git：
- 基础清理的内容通常已在 `.gitignore` 中
- 激进清理删除的文件也不应提交到仓库
- 推荐在 Git 仓库中只保留源代码和配置文件

## 🚀 自动化清理

### 添加到构建流程

在 `package.json` 中添加清理脚本：
```json
{
  "scripts": {
    "clean": "./cleanup.sh",
    "clean:aggressive": "./cleanup-aggressive.sh"
  }
}
```

### 定期清理

创建定期清理的 cron 任务：
```bash
# 每周运行基础清理
0 0 * * 0 cd /path/to/deer-flow && ./cleanup.sh
```

## ⚠️ 注意事项

1. **备份重要数据**：清理前备份 `outputs/` 目录中的重要文件
2. **网络依赖**：激进清理后首次安装需要网络连接
3. **安装时间**：重新安装依赖可能需要几分钟时间
4. **锁文件**：删除锁文件会导致依赖版本可能发生变化

## 🔍 检查工具

使用以下命令检查项目状态：

```bash
# 检查项目大小
du -sh .

# 检查各目录大小
du -sh */ | sort -hr

# 验证项目完整性
./check-deployment.sh

# 检查特定大文件
find . -size +10M -type f
```

通过合理使用这些清理工具，你可以根据需要优化 DeerFlow 项目的大小！ 