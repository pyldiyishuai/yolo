#!/bin/bash
# 视助系统一键启动脚本 (Linux / macOS)
# 使用方式: bash deploy/start.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "==================================="
echo "  视助系统 - 本地部署启动脚本"
echo "==================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
  echo "[错误] 未找到 python3，请先安装 Python 3.10+"
  exit 1
fi

# 安装后端依赖
echo "[1/3] 安装后端依赖..."
python3 -m pip install -r "$BACKEND/requirements.txt" -q

# 启动后端
echo "[2/3] 启动后端服务 (http://127.0.0.1:8000)..."
cd "$BACKEND"
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "  后端 PID: $BACKEND_PID"
sleep 2

# 启动前端
echo "[3/3] 启动前端开发服务器..."
if command -v npm &> /dev/null; then
  cd "$FRONTEND"
  [ ! -d node_modules ] && npm install --silent
  npm run dev &
  FRONTEND_PID=$!
  echo "  前端 PID: $FRONTEND_PID"
  sleep 3
  # 尝试打开浏览器
  if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
  elif command -v open &> /dev/null; then
    open http://localhost:5173
  fi
else
  echo "[警告] 未找到 npm，请手动进入 frontend/ 执行 npm run dev"
fi

echo ""
echo "✅ 视助系统已启动！"
echo "   前端地址: http://localhost:5173"
echo "   后端地址: http://127.0.0.1:8000"
echo "   API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
wait
