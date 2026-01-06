import os
import subprocess
import threading
import time
import shutil
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class DeviceInfo:
    """设备信息"""
    device_id: str
    platform: str  # 'iOS' or 'Android'
    name: str
    model: str
    os_version: str
    local_port: Optional[int] = None
    iproxy_pid: Optional[int] = None
    wda_pid: Optional[int] = None
    wda_status: str = 'stopped'  # 'stopped', 'starting', 'running', 'error'
    agent_instance: Optional[object] = None

class DeviceManager:
    """多设备管理器"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInfo] = {}
        self.port_pool = list(range(8100, 8200))  # 可用端口池
        self.used_ports = set()
        self.lock = threading.Lock()
        
    def allocate_port(self) -> Optional[int]:
        """分配一个可用端口"""
        with self.lock:
            for port in self.port_pool:
                if port not in self.used_ports:
                    self.used_ports.add(port)
                    return port
        return None
    
    def release_port(self, port: int):
        """释放端口"""
        with self.lock:
            if port in self.used_ports:
                self.used_ports.remove(port)
    
    def detect_ios_devices(self) -> List[DeviceInfo]:
        """检测 iOS 设备"""
        devices = []
        try:
            # 使用 idevice_id 获取所有连接的 iOS 设备
            result = subprocess.run(['idevice_id', '-l'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                udids = result.stdout.strip().split('\n')
                
                for udid in udids:
                    if not udid:
                        continue
                    
                    # 获取设备信息
                    info_result = subprocess.run(
                        ['ideviceinfo', '-u', udid, '-k', 'DeviceName'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    device_name = info_result.stdout.strip() if info_result.returncode == 0 else 'Unknown'
                    
                    # 获取设备型号
                    model_result = subprocess.run(
                        ['ideviceinfo', '-u', udid, '-k', 'ProductType'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    model = model_result.stdout.strip() if model_result.returncode == 0 else 'Unknown'
                    
                    # 获取系统版本
                    version_result = subprocess.run(
                        ['ideviceinfo', '-u', udid, '-k', 'ProductVersion'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    os_version = version_result.stdout.strip() if version_result.returncode == 0 else 'Unknown'
                    
                    device_info = DeviceInfo(
                        device_id=udid,
                        platform='iOS',
                        name=device_name,
                        model=model,
                        os_version=os_version
                    )
                    devices.append(device_info)
                    
        except Exception as e:
            print(f"Error detecting iOS devices: {e}")
        
        return devices
    
    def detect_android_devices(self) -> List[DeviceInfo]:
        """检测 Android 设备"""
        devices = []
        
        # 检查 adb 命令是否存在
        if not shutil.which('adb'):
            return devices  # 静默返回空列表，不打印错误
        
        try:
            # 使用 adb devices 获取所有连接的 Android 设备
            result = subprocess.run(['adb', 'devices', '-l'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
                
                for line in lines:
                    if not line.strip() or 'offline' in line:
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == 'device':
                        serial = parts[0]
                        
                        # 获取设备信息
                        name_result = subprocess.run(
                            ['adb', '-s', serial, 'shell', 'getprop', 'ro.product.model'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        device_name = name_result.stdout.strip() if name_result.returncode == 0 else 'Unknown'
                        
                        # 获取设备型号
                        model_result = subprocess.run(
                            ['adb', '-s', serial, 'shell', 'getprop', 'ro.product.brand'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        brand = model_result.stdout.strip() if model_result.returncode == 0 else 'Unknown'
                        
                        # 获取系统版本
                        version_result = subprocess.run(
                            ['adb', '-s', serial, 'shell', 'getprop', 'ro.build.version.release'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        os_version = version_result.stdout.strip() if version_result.returncode == 0 else 'Unknown'
                        
                        device_info = DeviceInfo(
                            device_id=serial,
                            platform='Android',
                            name=f"{brand} {device_name}",
                            model=device_name,
                            os_version=os_version
                        )
                        devices.append(device_info)
                        
        except Exception as e:
            print(f"Error detecting Android devices: {e}")
        
        return devices
    
    def detect_all_devices(self) -> List[DeviceInfo]:
        """检测所有设备（iOS + Android）"""
        all_devices = []
        all_devices.extend(self.detect_ios_devices())
        all_devices.extend(self.detect_android_devices())
        
        # 更新设备列表，保留已有设备的状态信息
        with self.lock:
            for device in all_devices:
                if device.device_id in self.devices:
                    # 保留原有的端口和进程信息
                    existing = self.devices[device.device_id]
                    device.local_port = existing.local_port
                    device.iproxy_pid = existing.iproxy_pid
                    device.wda_pid = existing.wda_pid
                    device.wda_status = existing.wda_status
                    device.agent_instance = existing.agent_instance
                
                self.devices[device.device_id] = device
        
        return all_devices
    
    def start_iproxy(self, device_id: str) -> bool:
        """为 iOS 设备启动 iproxy 端口转发"""
        # 先获取设备信息和分配端口（需要锁）
        with self.lock:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            if device.platform != 'iOS':
                return False
            
            # 如果已经有端口，检查进程是否还在运行
            if device.local_port and device.iproxy_pid:
                try:
                    os.kill(device.iproxy_pid, 0)  # 检查进程是否存在
                    return True  # 进程还在运行
                except OSError:
                    # 进程已死，释放端口
                    self.release_port(device.local_port)
                    device.iproxy_pid = None
            
            # 分配新端口
            port = self.allocate_port()
            if not port:
                print(f"No available port for device {device_id}")
                return False
        
        # 在锁外启动进程，避免阻塞
        try:
            # 启动 iproxy
            process = subprocess.Popen(
                ['iproxy', str(port), '8100', '-u', device_id],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 保存进程信息
            with self.lock:
                device.local_port = port
                device.iproxy_pid = process.pid
            
            print(f"✅ Started iproxy for {device_id} on port {port}, PID: {process.pid}")
            return True
                
        except Exception as e:
            print(f"❌ Error starting iproxy: {e}")
            with self.lock:
                self.release_port(port)
            return False
    
    def stop_iproxy(self, device_id: str) -> bool:
        """停止 iOS 设备的 iproxy"""
        with self.lock:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            
            if device.iproxy_pid:
                try:
                    os.kill(device.iproxy_pid, 9)
                    print(f"Stopped iproxy PID: {device.iproxy_pid}")
                except OSError:
                    pass
                
                device.iproxy_pid = None
            
            if device.local_port:
                self.release_port(device.local_port)
                device.local_port = None
            
            return True
    
    def start_wda(self, device_id: str, wda_project_path: str) -> bool:
        """启动 iOS 设备的 WebDriverAgent"""
        # 先检查设备和路径（需要锁）
        with self.lock:
            if device_id not in self.devices:
                print(f"❌ Device {device_id} not found in device list")
                return False
            
            device = self.devices[device_id]
            if device.platform != 'iOS':
                print(f"❌ Device {device_id} is not iOS platform")
                return False
            
            # 检查 WDA 项目路径
            if not os.path.exists(wda_project_path):
                print(f"❌ WDA project path does not exist: {wda_project_path}")
                return False
            
            xcodeproj_path = os.path.join(wda_project_path, 'WebDriverAgent.xcodeproj')
            if not os.path.exists(xcodeproj_path):
                print(f"❌ WebDriverAgent.xcodeproj not found at: {xcodeproj_path}")
                return False
            
            needs_iproxy = not device.local_port
        
        # 在锁外启动 iproxy，避免死锁
        if needs_iproxy:
            print(f"🔧 Starting iproxy for device {device_id}...")
            if not self.start_iproxy(device_id):
                print(f"❌ Failed to start iproxy for device {device_id}")
                return False
            print(f"✅ iproxy started")
        
        # 设置 WDA 状态
        with self.lock:
            device.wda_status = 'starting'
            print(f"🚀 Starting WDA for device {device_id}...")
        
        # 在后台线程启动 WDA
        def start_wda_thread():
            try:
                print(f"📱 Launching xcodebuild for device {device_id}...")
                print(f"   Project: {wda_project_path}/WebDriverAgent.xcodeproj")
                print(f"   Destination: id={device_id}")
                
                # 启动 xcodebuild
                process = subprocess.Popen(
                    [
                        'xcodebuild',
                        '-project', f'{wda_project_path}/WebDriverAgent.xcodeproj',
                        '-scheme', 'WebDriverAgentRunner',
                        '-destination', f'id={device_id}',
                        'test'
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=wda_project_path
                )
                
                with self.lock:
                    device.wda_pid = process.pid
                    device.wda_status = 'running'
                
                print(f"✅ WDA process started for {device_id}, PID: {process.pid}")
                
                # 等待进程结束
                stdout, stderr = process.communicate()
                returncode = process.returncode
                
                if returncode != 0:
                    print(f"❌ WDA exited with error code {returncode}")
                    if stderr:
                        error_msg = stderr.decode('utf-8', errors='ignore')[:500]
                        print(f"   Error output: {error_msg}")
                
                with self.lock:
                    device.wda_status = 'stopped'
                    device.wda_pid = None
                    
            except FileNotFoundError:
                print(f"❌ xcodebuild command not found. Please install Xcode Command Line Tools.")
                with self.lock:
                    device.wda_status = 'error'
                    device.wda_pid = None
            except Exception as e:
                print(f"❌ Error starting WDA: {e}")
                import traceback
                traceback.print_exc()
                with self.lock:
                    device.wda_status = 'error'
                    device.wda_pid = None
        
        thread = threading.Thread(target=start_wda_thread, daemon=True)
        thread.start()
        
        return True
    
    def stop_wda(self, device_id: str) -> bool:
        """停止 iOS 设备的 WebDriverAgent"""
        with self.lock:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            
            if device.wda_pid:
                try:
                    # 杀死 xcodebuild 进程
                    os.kill(device.wda_pid, 9)
                    print(f"Stopped WDA PID: {device.wda_pid}")
                except OSError:
                    pass
                
                device.wda_pid = None
            
            device.wda_status = 'stopped'
            return True
    
    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        """获取设备信息"""
        return self.devices.get(device_id)
    
    def get_wda_url(self, device_id: str) -> Optional[str]:
        """获取设备的 WDA URL"""
        device = self.get_device(device_id)
        if device and device.platform == 'iOS' and device.local_port:
            return f"http://localhost:{device.local_port}"
        return None
    
    def cleanup(self):
        """清理所有资源"""
        with self.lock:
            for device_id in list(self.devices.keys()):
                self.stop_wda(device_id)
                self.stop_iproxy(device_id)

# 全局设备管理器实例
device_manager = DeviceManager()
