# Phone-Agent-Web 快速使用指南

## 问题说明

**为什么自动启动 WDA 会失败？**

自动启动 WDA 需要运行 `xcodebuild test` 命令，这是一个长时间运行的进程，会导致：
1. HTTP 请求超时
2. 后端服务阻塞
3. 进程管理复杂

**解决方案：手动启动 WDA**

手动启动 WDA 更稳定可靠，只需要在 Xcode 中运行一次，之后 WDA 会一直在设备上运行。

## 完整使用流程

### 步骤 1：手动启动 WDA（首次或 WDA 停止时）

```bash
# 1. 打开 WebDriverAgent 项目
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent
open WebDriverAgent.xcodeproj

# 2. 在 Xcode 中：
#    - 选择你的 iOS 设备（顶部工具栏）
#    - 点击 Product -> Test（或按 Cmd+U）
#    - 等待 WDA 在设备上启动（看到 "Test session started" 即可）

# 3. 保持 Xcode 运行，WDA 会持续在设备上运行
```

### 步骤 2：启动后端服务

```bash
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/Phone-Agent-Web
./start_backend.sh
```

后端将运行在：`http://localhost:5001`

### 步骤 3：启动前端（新终端窗口）

```bash
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/Phone-Agent-Web/frontend-vue
npm run dev
```

前端将运行在：`http://localhost:5173`

### 步骤 4：在 Web 界面中使用

1. **打开浏览器**：访问 `http://localhost:5173`

2. **刷新设备列表**：点击"刷新设备"按钮

3. **选择设备**：点击你的设备卡片（会高亮显示）

4. **启动 WDA 连接**：
   - 点击"启动 WDA"按钮
   - 系统会自动启动 iproxy（端口转发）
   - 检测设备上的 WDA 是否运行
   - 如果 WDA 已运行，状态会变为"运行中"

5. **执行任务**：
   - 在指令输入框输入任务（如"打开设置"）
   - 点击"执行任务"
   - 查看实时日志和屏幕截图

## 常见问题

### Q1: 点击"启动 WDA"后一直加载？

**原因**：WDA 未在设备上运行

**解决**：
1. 在 Xcode 中手动启动 WDA（步骤 1）
2. 确保看到 "Test session started" 消息
3. 刷新浏览器页面
4. 再次点击"启动 WDA"

### Q2: 网站检测不到设备？

**原因**：后端服务未运行或设备未连接

**解决**：
```bash
# 检查后端服务
ps aux | grep "python.*backend"

# 如果没有运行，重启后端
./start_backend.sh

# 检查设备连接
idevice_id -l
```

### Q3: WDA 状态显示"已停止"？

**原因**：设备上的 WDA 进程已停止

**解决**：
1. 在 Xcode 中重新运行 Product -> Test
2. 等待 WDA 启动
3. 在 Web 界面点击"启动 WDA"

### Q4: 如何确认 WDA 正在运行？

在终端运行：
```bash
# 如果 WDA 正在运行，应该返回状态信息
curl http://localhost:8100/status
```

如果返回 JSON 数据，说明 WDA 正在运行。

## 架构说明

```
┌─────────────┐
│   浏览器     │ ← 用户界面（Vue 3）
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│  后端服务    │ ← Flask + DeviceManager
│  (port 5001) │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌─▼────┐
│iproxy│  │ AI   │
│8100  │  │Model │
└──┬───┘  └──────┘
   │ USB
┌──▼──────────┐
│  iOS 设备    │ ← WDA 运行在设备上
│  (WDA:8100) │
└─────────────┘
```

**关键点**：
- **WDA** 必须在设备上运行（通过 Xcode 启动）
- **iproxy** 由后端自动启动，负责端口转发
- **后端** 通过 iproxy 与设备上的 WDA 通信

## 停止服务

```bash
# 停止后端和前端
./stop-all.sh

# 或手动停止
pkill -f "python.*backend"
pkill -f "npm.*dev"
pkill -f "iproxy"
```

## 技巧

1. **保持 Xcode 运行**：WDA 会持续在设备上运行，无需重复启动
2. **检查日志**：后端终端会显示详细的操作日志
3. **重启设备**：如果 WDA 无响应，重启设备后重新在 Xcode 中运行
4. **端口冲突**：如果提示端口占用，运行 `pkill iproxy` 清理

## 下一步优化（可选）

如果需要完全自动化 WDA 启动，可以考虑：
1. 使用 `xcodebuild` 的 daemon 模式
2. 使用 `tidevice` 等第三方工具
3. 将 WDA 打包为独立 App 安装到设备

但目前的手动启动方式最稳定可靠。
