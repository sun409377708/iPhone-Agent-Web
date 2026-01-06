#!/usr/bin/env python3
"""快速测试后端 API"""

import requests
import json

def test_devices_api():
    """测试设备检测 API"""
    try:
        print("🔍 测试设备检测 API...")
        response = requests.get('http://localhost:5001/api/devices', timeout=5)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API 正常工作")
            print(f"   检测到 {len(data.get('devices', []))} 个设备:")
            for device in data.get('devices', []):
                print(f"      - {device['name']} ({device['platform']}) - {device['id'][:20]}...")
            return True
        else:
            print(f"   ❌ API 返回错误: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到后端服务 (端口 5001)")
        print("   请确保后端服务正在运行:")
        print("   ./start_backend.sh")
        return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def test_wda_start(device_id):
    """测试 WDA 启动 API"""
    try:
        print(f"\n🚀 测试 WDA 启动 API (设备: {device_id[:20]}...)...")
        response = requests.post(
            f'http://localhost:5001/api/devices/{device_id}/wda/start',
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ WDA 启动成功: {data.get('message')}")
                return True
            else:
                print(f"   ❌ WDA 启动失败: {data.get('error')}")
                return False
        else:
            print(f"   ❌ API 返回错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  后端 API 测试")
    print("=" * 60)
    print()
    
    # 测试设备检测
    if test_devices_api():
        # 获取第一个设备并测试 WDA 启动
        response = requests.get('http://localhost:5001/api/devices')
        devices = response.json().get('devices', [])
        if devices:
            ios_devices = [d for d in devices if d['platform'] == 'iOS']
            if ios_devices:
                test_wda_start(ios_devices[0]['id'])
            else:
                print("\n⚠️  没有检测到 iOS 设备")
    
    print()
    print("=" * 60)
