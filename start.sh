#!/bin/bash

# 确保脚本在 Phone-Agent-Web 目录下运行
cd "$(dirname "$0")"

echo "🚀 正在启动 Phone Agent Web 服务..."

# 检查并启动 iproxy (8100 端口转发)
IPROXY_PID=$(pgrep -f "iproxy 8100 8100")
if [ -z "$IPROXY_PID" ]; then
    echo "🔗 iproxy 未启动，正在后台启动 iproxy 8100 8100..."
    nohup iproxy 8100 8100 > /dev/null 2>&1 &
    sleep 2
else
    echo "✅ iproxy 已在运行 (PID: $IPROXY_PID)"
fi

# 检查并清理旧的 5001 端口进程 (避免端口占用)
OLD_PID=$(lsof -t -i:5001)
if [ ! -z "$OLD_PID" ]; then
    echo "⚠️ 检测到 5001 端口已被占用 (PID: $OLD_PID)，正在清理..."
    kill -9 $OLD_PID
    sleep 1
fi

# 设置代理 (根据你的环境配置)
export https_proxy=http://127.0.0.1:7897 
export http_proxy=http://127.0.0.1:7897 
export all_proxy=socks5://127.0.0.1:7897

echo "📡 代理已设置: $https_proxy"

# 获取并打印局域网 IP
LAN_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
echo "🔗 局域网访问地址: http://$LAN_IP:5001"
echo "🔗 本地访问地址: http://127.0.0.1:5001"

# 检查 Python 环境并运行
if command -v python3.11 &> /dev/null; then
    python3.11 run.py
elif command -v python3 &> /dev/null; then
    python3 run.py
else
    echo "❌ 错误: 未找到 Python 环境，请确保已安装 Python 3.11"
    exit 1
fi
