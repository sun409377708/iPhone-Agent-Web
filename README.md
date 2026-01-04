# Phone-Agent-Web

基于 AutoGLM 的智能 iOS 手机助理 Web 控制台。

## 🌟 项目简介
Phone-Agent-Web 是一个将 Open-AutoGLM 核心算法能力 Web 化的项目。它允许用户通过浏览器以自然语言下达指令，远程控制 iOS 设备完成各种复杂的自动化任务。

## 🧠 工作原理
系统的运作可以概括为 **“大脑 + 眼睛 + 手”** 的协同工作模式：
1. **眼睛 (WebDriverAgent/WDA)**：运行在 iOS 设备上，负责截取屏幕画面并回传，同时接收并执行点击、滑动等原始指令。
2. **大脑 (AI 豆包推理模型)**：接收屏幕截图和用户指令，通过多模态理解能力规划操作路径，并返回具体的动作指令（如 `Tap`, `Swipe`, `Launch`）。
3. **手 (Backend/Flask)**：作为中控系统，负责调用 AI 模型进行决策，并将决策翻译为 WDA 可执行的 API 请求，同时将整个思考和执行过程流式展示在 Web 前端。

## 🏗️ 架构设计
- **backend/**: 基于 Flask 的后端服务，负责处理任务调度、数据库交互及 AI 模型集成。
- **frontend/**: 简洁现代的 Web 控制台，支持流式日志显示和任务历史管理。
- **database/**: 使用 SQLite 持久化存储所有操作历史，确保数据不丢失。
- **Open-AutoGLM**: 作为核心算法库平级引用，解耦底层逻辑与业务功能。

## 🚀 启动指南

### 前置条件
1. 确保 iOS 设备已连接。
2. **启动 WebDriverAgent (WDA)**：
   - **方案 A (推荐)：使用命令行启动 (无需打开 Xcode UI)**
     在终端运行以下命令（替换 `[UDID]` 为你的设备 UDID，可通过 `idevice_id -l` 查看）：
     ```bash
     xcodebuild -project /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent/WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination "id=[UDID]" test
     ```
   - **方案 B：使用 tidevice (更简便)**
     安装：`pip install tidevice`
     运行：`tidevice wdaproxy -B com.facebook.WebDriverAgentRunner.xctrunner --port 8100`
3. 确保已通过 `iproxy 8100 8100` 完成端口转发（如果使用方案 A）。
4. 本地环境已安装 Python 3.11 及相关依赖。

### 启动步骤
1. **一键启动**：
   ```bash
   ./start.sh
   ```
2. **访问页面**：在浏览器打开终端输出的地址（默认为 `http://127.0.0.1:5001`）。

### 手动启动 (备选)
1. **开启代理**：
   ```bash
   export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897
   ```
2. **运行服务**：
   ```bash
   python3.11 run.py
   ```

## 🛑 停止服务
你可以运行停止脚本来一键关闭所有相关服务：
```bash
./stop.sh
```
或者在运行 `start.sh` 的终端窗口按下 `Ctrl + C` 停止 Web 服务。

---
*注：本项目仅供学习和研究使用。*
