#!/bin/bash
# 启动后端服务脚本

cd "$(dirname "$0")"

echo "🔍 检查端口 5001..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 5001 已被占用，正在停止旧进程..."
    lsof -ti:5001 | xargs kill -9
    sleep 1
fi

echo "🚀 启动后端服务..."
python3 -m backend.app

# 如果启动失败，尝试使用 python
if [ $? -ne 0 ]; then
    echo "⚠️  python3 启动失败，尝试使用 python..."
    python -m backend.app
fi
