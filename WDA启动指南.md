# WebDriverAgent 启动和连接指南

## 📋 前提条件

1. ✅ iOS 设备通过 USB 连接到 Mac
2. ✅ 设备已信任此电脑
3. ✅ WebDriverAgent 项目已配置好签名
4. ✅ 安装了 `libimobiledevice`（用于 iproxy）

---

## 🚀 完整启动流程

### 步骤 1：检查设备连接

```bash
# 查看已连接的设备
idevice_id -l

# 或使用 xcrun
xcrun devicectl list devices
```

**预期输出**：显示设备 UDID（如 `00008101-001D059E0481401E`）

---

### 步骤 2：启动 WebDriverAgent

#### 方法 A：使用 Xcode（推荐）

1. 打开 WebDriverAgent 项目：
   ```bash
   cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent
   open WebDriverAgent.xcodeproj
   ```

2. 在 Xcode 中：
   - 选择 `WebDriverAgentRunner` scheme
   - 选择你的 iOS 设备作为目标
   - 点击运行（▶️）或按 `Cmd + R`

3. 首次运行时，在设备上：
   - 前往 **设置 > 通用 > VPN与设备管理**
   - 信任开发者证书

4. 再次运行，等待控制台显示：
   ```
   ServerURLHere->http://<IP>:8100<-ServerURLHere
   ```

#### 方法 B：使用命令行

```bash
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent

# 获取设备 UDID
UDID=$(idevice_id -l | head -1)

# 运行 WebDriverAgent
xcodebuild -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=$UDID" \
  test
```

---

### 步骤 3：设置端口转发

在**新的终端窗口**中运行：

```bash
# 将设备的 8100 端口转发到本地 8100 端口
iproxy 8100 8100
```

**保持此终端窗口运行**，不要关闭。

---

### 步骤 4：验证 WDA 连接

```bash
# 测试连接
curl http://localhost:8100/status

# 预期输出：JSON 格式的设备状态信息
```

如果返回 JSON 数据，说明 WDA 已成功运行！

---

## 🔍 当前状态检查

### 检查 WebDriverAgent 是否运行

```bash
ps aux | grep WebDriverAgent
```

**当前状态**：
```
✅ WebDriverAgent 正在运行
   设备: 00008101-001D059E0481401E
   进程: xcodebuild (PID: 84530)
```

### 检查 iproxy 是否运行

```bash
ps aux | grep iproxy
```

**当前状态**：
```
✅ iproxy 正在运行 (PID: 84526)
   端口转发: 8100 -> 8100
```

### 检查 WDA 响应

```bash
curl -v http://localhost:8100/status
```

**当前问题**：
```
❌ Connection reset by peer
   原因：WDA 会话可能已过期或需要重新初始化
```

---

## 🔧 解决连接问题

### 问题：Connection reset by peer

**原因**：
1. WDA 会话超时
2. WebDriverAgent 需要重新启动
3. 设备锁屏或断开连接

**解决方案**：

#### 方案 1：重启 WebDriverAgent（推荐）

```bash
# 1. 停止当前的 WebDriverAgent
pkill -f WebDriverAgent

# 2. 重新运行
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent
UDID=$(idevice_id -l | head -1)
xcodebuild -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=$UDID" \
  test
```

#### 方案 2：在 Xcode 中重新运行

1. 在 Xcode 中停止当前运行（⏹️）
2. 重新点击运行（▶️）
3. 等待控制台显示 `ServerURLHere`

#### 方案 3：重启 iproxy

```bash
# 停止旧的 iproxy
pkill iproxy

# 重新启动
iproxy 8100 8100
```

---

## ✅ 验证成功的标志

### 1. WDA 状态检查成功

```bash
curl http://localhost:8100/status
```

**成功输出示例**：
```json
{
  "value": {
    "state": "success",
    "os": {
      "name": "iOS",
      "version": "17.0"
    },
    "ios": {
      "simulatorVersion": "17.0"
    },
    "build": {
      "time": "Jan 5 2026 10:46:00"
    }
  },
  "sessionId": null,
  "status": 0
}
```

### 2. 创建会话成功

```bash
curl -X POST http://localhost:8100/session \
  -H "Content-Type: application/json" \
  -d '{"capabilities": {"alwaysMatch": {}}}'
```

**成功输出**：返回包含 `sessionId` 的 JSON

### 3. 前端可以看到设备

访问 `http://localhost:5173/devices`，应该能看到设备信息。

---

## 🎯 完整测试流程

### 1. 启动所有服务

```bash
# 终端 1：启动 WebDriverAgent（Xcode 或命令行）
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent
xcodebuild -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=$(idevice_id -l | head -1)" \
  test

# 终端 2：启动 iproxy
iproxy 8100 8100

# 终端 3：启动后端
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/Phone-Agent-Web
python3 run.py

# 终端 4：启动前端
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/Phone-Agent-Web/frontend-vue
npm run dev
```

### 2. 测试连接

```bash
# 测试 WDA
curl http://localhost:8100/status

# 测试后端 API
curl http://localhost:5001/api/devices

# 访问前端
open http://localhost:5173
```

### 3. 执行任务

1. 访问 `http://localhost:5173/devices`
2. 输入任务：`打开设置`
3. 点击"执行任务"
4. 观察手机和日志输出

---

## 🐛 常见问题

### Q1: iproxy 命令找不到

```bash
# 安装 libimobiledevice
brew install libimobiledevice
```

### Q2: WebDriverAgent 签名失败

1. 打开 Xcode 项目
2. 选择 `WebDriverAgentLib` 和 `WebDriverAgentRunner` targets
3. 在 Signing & Capabilities 中选择你的开发团队
4. 修改 Bundle Identifier 为唯一值

### Q3: 设备未信任

1. 在设备上：设置 > 通用 > VPN与设备管理
2. 找到你的开发者证书
3. 点击"信任"

### Q4: 端口 8100 被占用

```bash
# 查找占用端口的进程
lsof -i :8100

# 杀死进程
kill -9 <PID>
```

---

## 📝 当前需要执行的操作

根据检查结果，你需要：

1. **重启 WebDriverAgent**（在 Xcode 中停止并重新运行）
2. **确保 iproxy 正在运行**（已经在运行，无需操作）
3. **测试 WDA 连接**（`curl http://localhost:8100/status`）
4. **刷新前端页面**（`http://localhost:5173/devices`）

---

**文档版本：v1.0**  
**更新日期：2026-01-05**
