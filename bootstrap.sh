#!/bin/bash

# Start both of DeerFlow's backend and web UI server.
# If the user presses Ctrl+C, kill them both.

# 检查并关闭 9000 和 9001 端口的进程
function kill_port() {
  local port=$1
  local pid
  pid=$(lsof -ti tcp:$port)
  if [ ! -z "$pid" ]; then
    echo "检测到端口 $port 被占用，正在关闭进程 $pid..."
    kill -9 $pid
    sleep 1
  fi
}

if [ "$1" = "--dev" -o "$1" = "-d" -o "$1" = "dev" -o "$1" = "development" ]; then
  echo -e "Starting DeerFlow in [DEVELOPMENT] mode...\n"

  # 先关闭端口
  kill_port 9000
  kill_port 9001

  # 检查是否存在 .env 文件，如果不存在则从 env.example 创建
  if [ ! -f .env ]; then
    echo "创建开发模式 .env 文件..."
    cp env.example .env
    # 修改为开发模式配置
    sed -i.bak 's|NEXT_PUBLIC_API_URL="http://localhost:8000/api"|NEXT_PUBLIC_API_URL="http://localhost:9001"|g' .env
    sed -i.bak 's|APP_ENV=development|APP_ENV=development|g' .env
    rm -f .env.bak
    echo "已创建开发模式 .env 文件"
  fi

  # 读取 .env 里的日志级别（如有）
  LOG_LEVEL=$(grep '^LOG_LEVEL=' .env | cut -d'=' -f2 | tr -d '"')
  if [ -z "$LOG_LEVEL" ]; then
    LOG_LEVEL="info"
  fi

  # 检查 Tavily API 密钥
  if [ ! -z "$TAVILY_API_KEY" ]; then
    sed -i.bak "s|TAVILY_API_KEY=tvly-xxx|TAVILY_API_KEY=$TAVILY_API_KEY|g" .env
    rm -f .env.bak
    echo "✅ 已设置 Tavily API 密钥，将优先使用 Tavily 搜索"
  else
    if grep -q "TAVILY_API_KEY=tvly-" .env && ! grep -q "TAVILY_API_KEY=tvly-xxx" .env; then
      echo "✅ 检测到已配置的 Tavily API 密钥"
    else
      echo "⚠️  未检测到 Tavily API 密钥，将使用 DuckDuckGo 作为回退搜索引擎"
      echo "   如需使用 Tavily，请运行: ./set-tavily-key.sh your_api_key"
    fi
  fi

  # 读取 conf.yaml 的模型信息（如有 conf.yaml）
  if [ -f conf.yaml ]; then
    BASIC_MODEL=$(grep '^  model:' conf.yaml | head -n1 | awk '{print $2}')
    echo "conf.yaml 中 BASIC_MODEL: $BASIC_MODEL"
  fi

  # 启动后端服务器 (端口 9001)
  echo "启动后端服务器..."
  uv run python server.py --port 9001 --reload --log-level $LOG_LEVEL & SERVER_PID=$!

  # 等待后端启动
  sleep 3

  # 启动前端服务器 (端口 9000)
  echo "启动前端服务器..."
  cd web && NEXT_PUBLIC_API_URL=http://localhost:9001/api pnpm dev --port 9000 & WEB_PID=$!
  cd ..

  echo "开发模式启动完成:"
  echo "  前端: http://localhost:9000"
  echo "  后端: http://localhost:9001"
  echo "  API 文档: http://localhost:9001/docs"
  echo "按 Ctrl+C 停止服务"

  # 更好的信号处理
  cleanup() {
    echo ""
    echo "正在停止服务..."
    kill $SERVER_PID $WEB_PID 2>/dev/null
    wait $SERVER_PID $WEB_PID 2>/dev/null
    echo "服务已停止"
    exit 0
  }

  trap cleanup SIGINT SIGTERM EXIT
  wait
else
  echo -e "Starting DeerFlow in [PRODUCTION] mode...\n"

  # 检查是否存在 .env 文件
  if [ ! -f .env ]; then
    echo "警告: 未找到 .env 文件，请从 env.example 复制并配置"
    echo "运行: cp env.example .env"
    echo "然后编辑 .env 文件设置您的 API 密钥"
    exit 1
  fi

  uv run server.py & SERVER_PID=$!
  cd web && pnpm start & WEB_PID=$!
  trap "kill $SERVER_PID $WEB_PID 2>/dev/null" SIGINT SIGTERM EXIT
  wait
fi
