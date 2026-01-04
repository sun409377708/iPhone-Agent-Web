#!/bin/bash

# 确保脚本在 Phone-Agent-Web 目录下运行
cd "$(dirname "$0")"

echo "🛑 正在停止 Phone Agent 相关服务..."

# 停止 Web 服务 (5001 端口)
WEB_PID=$(lsof -t -i:5001)
if [ ! -z "$WEB_PID" ]; then
    echo "关闭 Web 服务 (PID: $WEB_PID)..."
    kill -9 $WEB_PID
else
    echo "Web 服务未运行。"
fi

# 停止 iproxy
IPROXY_PID=$(pgrep -f "iproxy 8100 8100")
if [ ! -z "$IPROXY_PID" ]; then
    echo "关闭 iproxy (PID: $IPROXY_PID)..."
    kill -9 $IPROXY_PID
else
    echo "iproxy 未运行。"
fi

echo "✅ 所有相关服务已停止。"
