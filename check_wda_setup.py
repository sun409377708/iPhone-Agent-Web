#!/usr/bin/env python3
"""WDA 环境检查脚本"""

import os
import sys
import subprocess
import shutil

def check_command(cmd):
    """检查命令是否可用"""
    return shutil.which(cmd) is not None

def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("  WebDriverAgent 环境检查")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 1. 检查 Xcode
    print("1️⃣  检查 Xcode...")
    if check_command('xcodebuild'):
        success, output = run_command(['xcodebuild', '-version'])
        if success:
            version = output.split('\n')[0]
            print(f"   ✅ Xcode 已安装: {version}")
        else:
            print(f"   ⚠️  Xcode 已安装但无法获取版本")
    else:
        print("   ❌ xcodebuild 命令未找到")
        print("   请安装 Xcode Command Line Tools:")
        print("   xcode-select --install")
        all_ok = False
    print()
    
    # 2. 检查 libimobiledevice
    print("2️⃣  检查 libimobiledevice (iOS 设备工具)...")
    if check_command('idevice_id'):
        success, output = run_command(['idevice_id', '-l'])
        if success:
            devices = output.split('\n') if output else []
            device_count = len([d for d in devices if d.strip()])
            print(f"   ✅ libimobiledevice 已安装")
            print(f"   📱 检测到 {device_count} 个 iOS 设备")
            if device_count > 0:
                for device in devices:
                    if device.strip():
                        print(f"      - {device}")
        else:
            print(f"   ⚠️  libimobiledevice 已安装但无法列出设备")
    else:
        print("   ❌ idevice_id 命令未找到")
        print("   请安装 libimobiledevice:")
        print("   brew install libimobiledevice")
        all_ok = False
    print()
    
    # 3. 检查 iproxy
    print("3️⃣  检查 iproxy (端口转发工具)...")
    if check_command('iproxy'):
        print("   ✅ iproxy 已安装")
    else:
        print("   ❌ iproxy 命令未找到")
        print("   请安装 usbmuxd:")
        print("   brew install usbmuxd")
        all_ok = False
    print()
    
    # 4. 检查 WebDriverAgent 项目
    print("4️⃣  检查 WebDriverAgent 项目...")
    wda_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'WebDriverAgent'))
    if os.path.exists(wda_path):
        print(f"   ✅ WebDriverAgent 目录存在: {wda_path}")
        
        xcodeproj = os.path.join(wda_path, 'WebDriverAgent.xcodeproj')
        if os.path.exists(xcodeproj):
            print(f"   ✅ WebDriverAgent.xcodeproj 存在")
        else:
            print(f"   ❌ WebDriverAgent.xcodeproj 未找到")
            all_ok = False
    else:
        print(f"   ❌ WebDriverAgent 目录不存在: {wda_path}")
        print("   请克隆 WebDriverAgent 项目:")
        print("   cd /Users/jianqin/Desktop/ModelTrain/Open-GLM")
        print("   git clone https://github.com/appium/WebDriverAgent.git")
        all_ok = False
    print()
    
    # 5. 检查 ADB (Android)
    print("5️⃣  检查 ADB (Android 设备工具)...")
    if check_command('adb'):
        success, output = run_command(['adb', 'devices'])
        if success:
            lines = output.split('\n')[1:]  # 跳过第一行 "List of devices attached"
            devices = [l for l in lines if l.strip() and '\tdevice' in l]
            print(f"   ✅ ADB 已安装")
            print(f"   🤖 检测到 {len(devices)} 个 Android 设备")
            for device in devices:
                serial = device.split('\t')[0]
                print(f"      - {serial}")
        else:
            print(f"   ⚠️  ADB 已安装但无法列出设备")
    else:
        print("   ⚠️  adb 命令未找到 (可选，仅 Android 需要)")
        print("   如需支持 Android，请安装 Android SDK Platform Tools")
    print()
    
    # 总结
    print("=" * 60)
    if all_ok:
        print("✅ 所有必需组件已就绪！")
        print()
        print("下一步:")
        print("1. 确保 iOS 设备已通过 USB 连接并信任此电脑")
        print("2. 在 Xcode 中打开 WebDriverAgent 项目并配置签名")
        print("3. 启动后端服务器")
        print("4. 在前端点击'启动 WDA'按钮")
    else:
        print("❌ 部分组件缺失，请按照上述提示安装")
    print("=" * 60)

if __name__ == '__main__':
    main()
