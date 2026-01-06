# WebDriverAgent 配置指南

## 前置条件检查

运行环境检查脚本：
```bash
python3 check_wda_setup.py
```

## 配置步骤

### 1. 在 Xcode 中配置签名

1. 打开 WebDriverAgent 项目：
   ```bash
   cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent
   open WebDriverAgent.xcodeproj
   ```

2. 在 Xcode 中选择 `WebDriverAgentRunner` target

3. 在 "Signing & Capabilities" 选项卡中：
   - 勾选 "Automatically manage signing"
   - 选择你的 Apple ID 对应的 Team
   - 如果没有 Team，需要先添加 Apple ID（Xcode -> Preferences -> Accounts）

4. 对 `WebDriverAgentLib` target 重复上述步骤

5. 修改 Bundle Identifier（避免冲突）：
   - 将 `com.facebook.WebDriverAgentRunner` 改为 `com.yourname.WebDriverAgentRunner`
   - 将 `com.facebook.WebDriverAgentLib` 改为 `com.yourname.WebDriverAgentLib`

### 2. 首次手动运行（重要）

第一次必须在 Xcode 中手动运行一次：

1. 连接 iOS 设备
2. 在 Xcode 顶部选择你的设备
3. 选择 Product -> Test（或按 Cmd+U）
4. 在设备上信任开发者证书：
   - 设置 -> 通用 -> VPN与设备管理 -> 开发者App
   - 点击你的 Apple ID
   - 点击"信任"

### 3. 验证 WDA 是否运行

手动测试 WDA：
```bash
# 启动 iproxy（端口转发）
iproxy 8100 8100 -u <你的设备UDID>

# 在另一个终端测试 WDA
curl http://localhost:8100/status
```

如果返回 JSON 数据，说明 WDA 正常运行。

### 4. 通过 Web 界面启动

配置完成后，就可以在 Web 界面点击"启动 WDA"按钮了。

## 常见问题

### Q1: "Failed to start WDA"
**原因**: WebDriverAgent 项目未配置签名或首次未手动运行

**解决**: 按照上述步骤 1-2 在 Xcode 中配置并首次手动运行

### Q2: "xcodebuild command not found"
**原因**: 未安装 Xcode Command Line Tools

**解决**:
```bash
xcode-select --install
```

### Q3: 设备未检测到
**原因**: libimobiledevice 未安装或设备未信任

**解决**:
```bash
# 安装 libimobiledevice
brew install libimobiledevice

# 检查设备
idevice_id -l
```

### Q4: "Could not find developer disk image"
**原因**: iOS 版本太新，Xcode 版本太旧

**解决**: 升级 Xcode 到最新版本

### Q5: WDA 启动后立即退出
**原因**: 可能是签名问题或设备未信任证书

**解决**:
1. 检查 Xcode 中的签名配置
2. 在设备上信任开发者证书
3. 查看后端日志获取详细错误信息

## 查看后端日志

启动后端时会输出详细的 WDA 启动日志：
```bash
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/Phone-Agent-Web
python3 -m backend.app
```

关注以下日志：
- `🚀 Starting WDA for device...` - WDA 开始启动
- `✅ WDA process started...` - WDA 进程已启动
- `❌ WDA exited with error code...` - WDA 启动失败

## 自动化脚本

如果经常需要重启 WDA，可以使用以下脚本：

```bash
#!/bin/bash
# restart_wda.sh

DEVICE_ID=$(idevice_id -l | head -n 1)
echo "Device: $DEVICE_ID"

# 停止旧的 iproxy
pkill -f "iproxy 8100"

# 启动新的 iproxy
iproxy 8100 8100 -u $DEVICE_ID &

# 等待端口就绪
sleep 2

# 启动 WDA
cd /Users/jianqin/Desktop/ModelTrain/Open-GLM/WebDriverAgent
xcodebuild -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination "id=$DEVICE_ID" \
  test
```

## 参考资料

- [WebDriverAgent 官方文档](https://github.com/appium/WebDriverAgent)
- [iOS 真机测试配置](https://appium.io/docs/en/drivers/ios-xcuitest-real-devices/)
