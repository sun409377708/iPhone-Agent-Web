#!/bin/bash

# Phone-Agent-Web 一键启动脚本
# 启动所有必要的服务：WebDriverAgent、iproxy、Flask 后端、Vue 前端

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Phone-Agent-Web 一键启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查并启动 iproxy
echo -e "${YELLOW}[1/4] 检查 iproxy 端口转发...${NC}"
IPROXY_PID=$(pgrep -f "iproxy 8100 8100" || true)
if [ -z "$IPROXY_PID" ]; then
    echo "  启动 iproxy 8100 8100..."
    nohup iproxy 8100 8100 > /dev/null 2>&1 &
    sleep 2
    echo -e "  ${GREEN}✅ iproxy 已启动${NC}"
else
    echo -e "  ${GREEN}✅ iproxy 已在运行 (PID: $IPROXY_PID)${NC}"
fi

# 2. 检查并启动 WebDriverAgent
echo -e "${YELLOW}[2/4] 检查 WebDriverAgent...${NC}"
if curl -s http://localhost:8100/status > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ WebDriverAgent 已在运行${NC}"
else
    echo -e "  ${RED}❌ WebDriverAgent 未运行${NC}"
    echo "  请在 Xcode 中手动启动 WebDriverAgent，或运行："
    echo "  cd ~/Desktop/ModelTrain/Open-GLM/WebDriverAgent"
    echo "  xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination \"id=\$(idevice_id -l | head -1)\" test"
    echo ""
    read -p "  按回车键继续（如果已在其他终端启动 WDA）..."
fi

# 3. 启动 Flask 后端
echo -e "${YELLOW}[3/4] 启动 Flask 后端...${NC}"
# 检查并清理旧的后端进程
OLD_BACKEND_PID=$(lsof -t -i:5001 || true)
if [ ! -z "$OLD_BACKEND_PID" ]; then
    echo "  清理旧的后端进程 (PID: $OLD_BACKEND_PID)..."
    kill -9 $OLD_BACKEND_PID 2>/dev/null || true
    sleep 1
fi

# 启动后端
echo "  启动 Flask 后端 (端口 5001)..."
nohup python3 run.py > backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# 检查后端是否启动成功
if curl -s http://127.0.0.1:5001/api/devices > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Flask 后端已启动 (PID: $BACKEND_PID)${NC}"
else
    echo -e "  ${RED}❌ Flask 后端启动失败，请查看 backend.log${NC}"
    exit 1
fi

# 4. 启动 Vue 前端
echo -e "${YELLOW}[4/4] 启动 Vue 前端...${NC}"
cd frontend-vue

# 检查并清理旧的前端进程
OLD_FRONTEND_PID=$(lsof -t -i:5173 || true)
if [ ! -z "$OLD_FRONTEND_PID" ]; then
    echo "  清理旧的前端进程 (PID: $OLD_FRONTEND_PID)..."
    kill -9 $OLD_FRONTEND_PID 2>/dev/null || true
    sleep 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "  安装前端依赖..."
    npm install
fi

# 启动前端
echo "  启动 Vue 开发服务器 (端口 5173)..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 5

# 检查前端是否启动成功
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Vue 前端已启动 (PID: $FRONTEND_PID)${NC}"
else
    echo -e "  ${RED}❌ Vue 前端启动失败，请查看 frontend.log${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# 完成
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 所有服务已启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 服务状态：${NC}"
echo "  • iproxy:        运行中 (8100 -> 8100)"
echo "  • WebDriverAgent: http://localhost:8100"
echo "  • Flask 后端:    http://127.0.0.1:5001"
echo "  • Vue 前端:      http://localhost:5173"
echo ""
echo -e "${BLUE}🌐 本地访问地址：${NC}"
echo -e "  ${GREEN}http://localhost:5173${NC}"
echo ""
echo -e "${BLUE}🌐 局域网访问地址：${NC}"
LAN_IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo "未获取到IP")
echo -e "  ${GREEN}http://${LAN_IP}:5173${NC}"
echo -e "  ${YELLOW}(局域网内其他设备可通过此地址访问)${NC}"
echo ""
echo -e "${YELLOW}📝 日志文件：${NC}"
echo "  • 后端日志: backend.log"
echo "  • 前端日志: frontend.log"
echo ""
echo -e "${YELLOW}⚠️  停止服务：${NC}"
echo "  运行: ./stop-all.sh"
echo ""
