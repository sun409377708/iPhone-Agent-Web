# Phone-Agent-Web

基于 Vue 3 + Flask + WebDriverAgent 的 iOS/Android 自动化测试平台。

通过自然语言控制手机，实现智能化的自动化测试。手机助理 Web 控制台。

## 🌟 项目简介
Phone-Agent-Web 是一个将 Open-AutoGLM 核心算法能力 Web 化的项目。它允许用户通过浏览器以自然语言下达指令，远程控制 iOS 设备完成各种复杂的自动化任务。

## 🧠 工作原理
系统的运作可以概括为 **“大脑 + 眼睛 + 手”** 的协同工作模式：
1. **眼睛 (WebDriverAgent/WDA)**：运行在 iOS 设备上，负责截取屏幕画面并回传，同时接收并执行点击、滑动等原始指令。
2. **大脑 (AI 豆包推理模型)**：接收屏幕截图和用户指令，通过多模态理解能力规划操作路径，并返回具体的动作指令（如 `Tap`, `Swipe`, `Launch`）。
3. **手 (Backend/Flask)**：作为中控系统，负责调用 AI 模型进行决策，并将决策翻译为 WDA 可执行的 API 请求，同时将整个思考和执行过程流式展示在 Web 前端。

## 🏗️ 架构设计
- **backend/**: 基于 Flask 的后端服务，负责处理任务调度、数据库交互及 AI 模型集成。
- **frontend-vue/**: Vue 3 前端，提供现代化的 Web 控制台，支持实时日志显示和任务历史管理。
- **database/**: 使用 SQLite 持久化存储所有操作历史，确保数据不丢失。
- **Open-AutoGLM**: 作为核心算法库平级引用，解耦底层逻辑与业务功能。

## 🚀 快速启动

### 1. 启动后端服务
```bash
./start_backend.sh
```

后端将运行在：**http://localhost:5001**

### 2. 启动前端（另一个终端）
```bash
cd frontend-vue
npm run dev
```

前端将运行在：**http://localhost:5173**

### 3. 访问 Web 界面
打开浏览器访问：**http://localhost:5173**

## 📱 多设备支持

当前版本支持：
- ✅ **iOS 设备**：通过 WebDriverAgent 完全支持
- ⚠️ **Android 设备**：设备检测已实现，任务执行功能待实现

### iOS 设备使用步骤

1. **检查环境**（首次使用）
   ```bash
   python3 check_wda_setup.py
   ```

2. **连接设备**
   - 通过 USB 连接 iOS 设备
   - 确保设备已信任此电脑

3. **配置 WDA**（首次使用）
   - 参考 `WDA_SETUP_GUIDE.md` 配置签名
   - 在 Xcode 中首次手动运行 WDA

4. **使用 Web 界面**
   - 刷新设备列表
   - 选择设备（点击设备卡片）
   - 点击"启动 WDA"按钮
   - 输入任务指令并执行

### 一键停止
```bash
./stop-all.sh
```

### 前置条件
1. iOS 设备已通过 USB 连接
2. 已安装 Node.js 和 npm
3. 已安装 Python 3.9+
4. WebDriverAgent 已在 Xcode 中运行

### 详细启动步骤

#### 1. 启动 WebDriverAgent
在 Xcode 中打开并运行 WebDriverAgent 项目，或使用命令行：
```bash
cd ~/Desktop/ModelTrain/Open-GLM/WebDriverAgent
xcodebuild -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=$(idevice_id -l | head -1)" \
  test
```

#### 2. 启动端口转发
```bash
iproxy 8100 8100
```

#### 3. 启动后端
```bash
python3 run.py
```

#### 4. 启动前端
```bash
cd frontend-vue
npm install  # 首次运行需要
npm run dev
```

## 📚 文档

- **使用说明.md** - 完整的使用指南
- **WDA启动指南.md** - WebDriverAgent 启动和故障排查
- **脚本说明.md** - Shell 脚本详细说明
- **开发指导文档.md** - 开发文档
- **UI设计规范.md** - UI 设计规范

---
*注：本项目仅供学习和研究使用。*
