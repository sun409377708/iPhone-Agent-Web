#!/bin/bash

# Phone-Agent-Web 一键停止脚本
# 停止所有服务：Vue 前端、Flask 后端、iproxy

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Phone-Agent-Web 一键停止${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 停止 Vue 前端 (5173 端口)
echo -e "${YELLOW}[1/3] 停止 Vue 前端...${NC}"
FRONTEND_PID=$(lsof -t -i:5173 || true)
if [ ! -z "$FRONTEND_PID" ]; then
    echo "  停止 Vue 前端 (PID: $FRONTEND_PID)..."
    kill -9 $FRONTEND_PID 2>/dev/null || true
    echo -e "  ${GREEN}✅ Vue 前端已停止${NC}"
else
    echo "  Vue 前端未运行"
fi

# 同时停止可能的 npm 进程
NPM_PIDS=$(pgrep -f "npm run dev" || true)
if [ ! -z "$NPM_PIDS" ]; then
    echo "  停止 npm 进程..."
    echo "$NPM_PIDS" | xargs kill -9 2>/dev/null || true
fi

# 2. 停止 Flask 后端 (5001 端口)
echo -e "${YELLOW}[2/3] 停止 Flask 后端...${NC}"
BACKEND_PID=$(lsof -t -i:5001 || true)
if [ ! -z "$BACKEND_PID" ]; then
    echo "  停止 Flask 后端 (PID: $BACKEND_PID)..."
    kill -9 $BACKEND_PID 2>/dev/null || true
    echo -e "  ${GREEN}✅ Flask 后端已停止${NC}"
else
    echo "  Flask 后端未运行"
fi

# 同时停止可能的 python 进程
PYTHON_PIDS=$(pgrep -f "python3 run.py" || true)
if [ ! -z "$PYTHON_PIDS" ]; then
    echo "  停止 Python 进程..."
    echo "$PYTHON_PIDS" | xargs kill -9 2>/dev/null || true
fi

# 3. 停止 iproxy
echo -e "${YELLOW}[3/3] 停止 iproxy...${NC}"
IPROXY_PID=$(pgrep -f "iproxy 8100 8100" || true)
if [ ! -z "$IPROXY_PID" ]; then
    echo "  停止 iproxy (PID: $IPROXY_PID)..."
    kill -9 $IPROXY_PID 2>/dev/null || true
    echo -e "  ${GREEN}✅ iproxy 已停止${NC}"
else
    echo "  iproxy 未运行"
fi

# 注意：不停止 WebDriverAgent，因为它可能在 Xcode 中运行
echo ""
echo -e "${YELLOW}⚠️  注意：${NC}"
echo "  WebDriverAgent 未停止（如在 Xcode 中运行，请手动停止）"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 所有服务已停止！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
