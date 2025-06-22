#!/bin/bash

# Start both of DeerFlow's backend and web UI server.
# If the user presses Ctrl+C, kill them both.

if [ "$1" = "--dev" -o "$1" = "-d" -o "$1" = "dev" -o "$1" = "development" ]; then
  echo -e "Starting DeerFlow in [DEVELOPMENT] mode...\n"
  
  # 创建开发模式专用的 .env 文件
  echo "# 开发模式环境变量 (自动生成)" > .env
  echo "NEXT_PUBLIC_API_URL=http://localhost:9001" >> .env
  echo "NODE_ENV=development" >> .env
  echo "SKIP_ENV_VALIDATION=true" >> .env
  
  # 启动后端服务器 (端口 9001)
  uv run python server.py --port 9001 --reload & SERVER_PID=$!
  
  # 启动前端服务器 (端口 9000)
  cd web && NEXT_PUBLIC_API_URL=http://localhost:9001 pnpm dev --port 9000 & WEB_PID=$!
  
  echo "开发模式启动完成:"
  echo "  前端: http://localhost:9000"
  echo "  后端: http://localhost:9001"
  echo "按 Ctrl+C 停止服务"
  
  trap "kill $SERVER_PID $WEB_PID 2>/dev/null" SIGINT SIGTERM EXIT
  wait
else
  echo -e "Starting DeerFlow in [PRODUCTION] mode...\n"
  
  # 检查是否存在 .env 文件
  if [ ! -f .env ]; then
    echo "警告: 未找到 .env 文件，请从 env.template 复制并配置"
    echo "运行: cp env.template .env"
    exit 1
  fi
  
  uv run server.py & SERVER_PID=$!
  cd web && pnpm start & WEB_PID=$!
  trap "kill $SERVER_PID $WEB_PID 2>/dev/null" SIGINT SIGTERM EXIT
  wait
fi
