#!/bin/bash

# 确保脚本在 Phone-Agent-Web 目录下运行
cd "$(dirname "$0")"

echo "🚀 正在启动 Phone Agent Web 服务..."

# 检查并启动 WebDriverAgent
echo "🔧 检查 WebDriverAgent 状态..."

# 检查 WDA 是否已运行
if curl -s http://localhost:8100/status > /dev/null 2>&1; then
    echo "✅ WebDriverAgent 已在运行"
else
    echo "🚀 WebDriverAgent 未运行，正在启动..."
    
    # 获取设备 UDID
    DEVICE_UDID=$(idevice_id -l 2>/dev/null | head -1)
    
    if [ -z "$DEVICE_UDID" ]; then
        echo "❌ 未检测到 iOS 设备，请确保设备已连接并信任此电脑"
        exit 1
    fi
    
    echo "   检测到设备: $DEVICE_UDID"
    
    # 使用 iproxy + xcodebuild 方式（更稳定）
    echo "   使用 iproxy + xcodebuild 启动 WDA..."
    
    # 1. 启动 iproxy
    IPROXY_PID=$(pgrep -f "iproxy 8100 8100")
    if [ -z "$IPROXY_PID" ]; then
        echo "   启动 iproxy 8100 8100..."
        nohup iproxy 8100 8100 > /dev/null 2>&1 &
        sleep 2
        echo "   iproxy 已启动"
    else
        echo "   iproxy 已在运行 (PID: $IPROXY_PID)"
    fi
    
    # 2. 启动 xcodebuild
    WDA_PROJECT="$HOME/Desktop/ModelTrain/Open-GLM/WebDriverAgent/WebDriverAgent.xcodeproj"
    
    if [ -f "$WDA_PROJECT/project.pbxproj" ]; then
        echo "   启动 xcodebuild..."
        nohup xcodebuild \
            -project "$WDA_PROJECT" \
            -scheme WebDriverAgentRunner \
            -destination "id=$DEVICE_UDID" \
            test > wda.log 2>&1 &
        
        WDA_PID=$!
        echo "   xcodebuild 已启动 (PID: $WDA_PID)"
        
        # 等待 WDA 启动
        echo "   等待 WDA 就绪（最多 60 秒）..."
        for i in {1..60}; do
            if curl -s http://localhost:8100/status > /dev/null 2>&1; then
                echo ""
                echo "✅ WebDriverAgent 启动成功"
                break
            fi
            sleep 1
            echo -n "."
        done
        echo ""
        
        # 检查是否启动成功
        if ! curl -s http://localhost:8100/status > /dev/null 2>&1; then
            echo "⚠️  WDA 启动超时，请检查日志: wda.log"
            echo "   提示: 可能需要在 Xcode 中手动运行 WebDriverAgent 项目"
        fi
    else
        echo "❌ 未找到 WebDriverAgent 项目: $WDA_PROJECT"
        echo "   请确保 WebDriverAgent 已克隆到正确位置"
        exit 1
    fi
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
