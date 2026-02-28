import os
import sys
import json
import threading
import queue
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from .models import db, TaskHistory, TestCase
from .config import Config
from .device_manager import device_manager, DeviceInfo

# Add Open-AutoGLM directory to path to import phone_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Open-AutoGLM')))

from phone_agent.agent_ios import IOSAgentConfig, IOSPhoneAgent
from phone_agent.model import ModelConfig

# Android Agent 暂未实现，使用条件导入
try:
    from phone_agent.agent_android import AndroidAgentConfig, AndroidPhoneAgent
    ANDROID_SUPPORT = True
except ImportError:
    ANDROID_SUPPORT = False
    print("⚠️  Android Agent not available. Only iOS devices are supported.")

# Configure template and static folders
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, '..', 'frontend'))
db_dir = os.path.abspath(os.path.join(current_dir, '..', 'database'))

app = Flask(__name__, 
            template_folder=os.path.join(frontend_dir, 'templates'),
            static_folder=os.path.join(frontend_dir, 'static'))
# 配置 CORS 允许所有来源访问（开发环境）
CORS(app, resources={r"/*": {"origins": "*"}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_dir, "phone_agent.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Global agent instance
agent = None
log_queue = queue.Queue()

class StreamLogger:
    def __init__(self, q):
        self.q = q
    def write(self, message):
        if message.strip():
            self.q.put(message)
    def flush(self):
        pass

# 注释掉 stdout 重定向，避免阻塞 Agent 执行
# sys.stdout = StreamLogger(log_queue)

with app.app_context():
    db.create_all()

def get_agent():
    global agent
    if agent is None:
        model_config = ModelConfig(
            base_url=Config.MODEL_BASE_URL,
            api_key=Config.MODEL_API_KEY,
            model_name=Config.MODEL_NAME
        )
        agent_config = IOSAgentConfig(
            wda_url=Config.WDA_URL,
            lang=Config.DEFAULT_LANG
        )
        agent = IOSPhoneAgent(model_config=model_config, agent_config=agent_config)
    return agent

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取所有连接的设备（iOS + Android）"""
    try:
        all_devices = device_manager.detect_all_devices()
        devices_list = []

        for device in all_devices:
            device_dict = {
                'id': device.device_id,
                'name': device.name,
                'platform': device.platform,
                'model': device.model,
                'version': device.os_version,
                'status': 'online'
            }

            if device.platform == 'iOS':
                device_dict['wda_status'] = device.wda_status
                device_dict['local_port'] = device.local_port
                device_dict['local_mjpeg_port'] = device.local_mjpeg_port
                device_dict['has_iproxy'] = device.iproxy_pid is not None

            devices_list.append(device_dict)

        return jsonify({'devices': devices_list})
    except Exception as e:
        print(f"Error detecting devices: {e}")
        return jsonify({'devices': [], 'error': str(e)})

@app.route('/api/history', methods=['GET'])
def get_history():
    history = TaskHistory.query.order_by(TaskHistory.created_at.desc()).limit(20).all()
    return jsonify([task.to_dict() for task in history])


@app.route('/api/devices/<device_id>/wda/start', methods=['POST'])
def start_device_wda(device_id):
    """启动 iOS 设备的 WebDriverAgent"""
    try:
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        if device.platform != 'iOS':
            return jsonify({'success': False, 'error': 'WDA only supports iOS devices'}), 400

        wda_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'WebDriverAgent'))
        success = device_manager.start_wda(device_id, wda_path)
        if success:
            return jsonify({'success': True, 'message': 'WDA is starting, please wait...'})
        return jsonify({'success': False, 'error': 'Failed to start WDA. Check backend logs for details.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<device_id>/wda/stop', methods=['POST'])
def stop_device_wda(device_id):
    """停止 iOS 设备的 WebDriverAgent"""
    try:
        success = device_manager.stop_wda(device_id)
        if success:
            return jsonify({'success': True, 'message': 'WDA stopped'})
        return jsonify({'success': False, 'error': 'Failed to stop WDA'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<device_id>/wda/status', methods=['GET'])
def get_device_wda_status(device_id):
    """获取 iOS 设备的 WDA 状态"""
    try:
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404

        return jsonify({
            'success': True,
            'status': device.wda_status,
            'has_iproxy': device.iproxy_pid is not None,
            'local_port': device.local_port
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/screenshot', methods=['GET'])
def get_screenshot():
    """获取设备截图（支持多设备）"""
    device_id = request.args.get('device_id')
    try:
        import requests
        import base64
        from io import BytesIO
        from PIL import Image

        device = device_manager.get_device(device_id) if device_id else None

        if device and device.platform == 'iOS':
            wda_url = device_manager.get_wda_url(device_id)
            if not wda_url:
                return jsonify({'success': False, 'error': 'WDA not available'}), 500
            response = requests.get(f"{wda_url}/screenshot", timeout=10)
        elif device and device.platform == 'Android':
            import subprocess
            result = subprocess.run(
                ['adb', '-s', device_id, 'exec-out', 'screencap', '-p'],
                capture_output=True,
                timeout=10
            )
            if result.returncode != 0:
                return jsonify({'success': False, 'error': 'Failed to capture screenshot'}), 500
            img_data = result.stdout
            img = Image.open(BytesIO(img_data))
            max_width = 400
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.convert('RGB').save(buffer, format='JPEG', quality=85)
            screenshot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return jsonify({'success': True, 'image': f'data:image/jpeg;base64,{screenshot_data}'})
        else:
            response = requests.get(f"{Config.WDA_URL}/screenshot", timeout=10)

        if response.status_code == 200:
            data = response.json()
            screenshot_base64 = data.get('value', '')
            
            if not screenshot_base64:
                return jsonify({
                    'success': False,
                    'error': 'No screenshot data in WDA response'
                }), 500
            
            # 解码 base64 图片
            img_data = base64.b64decode(screenshot_base64)
            img = Image.open(BytesIO(img_data))
            
            # 调整大小到合适的显示尺寸
            max_width = 400
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为 JPEG 以减小大小
            buffer = BytesIO()
            img.convert('RGB').save(buffer, format='JPEG', quality=85)
            screenshot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'image': f'data:image/jpeg;base64,{screenshot_data}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'WDA returned status code {response.status_code}'
            }), 500
    except Exception as e:
        import traceback
        print(f"Screenshot error: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/devices/<device_id>/mjpeg', methods=['GET'])
def get_mjpeg_stream(device_id):
    """获取 iOS 设备 MJPEG 实时流（代理 WDA 9100 端口）"""
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({'success': False, 'error': 'Device not found'}), 404
    if device.platform != 'iOS':
        return jsonify({'success': False, 'error': 'MJPEG stream only supports iOS devices'}), 400

    mjpeg_url = device_manager.get_mjpeg_url(device_id)
    if not mjpeg_url:
        return jsonify({'success': False, 'error': 'MJPEG iproxy not available'}), 500

    import requests
    try:
        upstream = requests.get(mjpeg_url, stream=True, timeout=(3, 60))
    except requests.RequestException as e:
        return jsonify({'success': False, 'error': f'Failed to connect MJPEG stream: {e}'}), 502

    if upstream.status_code != 200:
        upstream.close()
        return jsonify({'success': False, 'error': f'WDA MJPEG returned {upstream.status_code}'}), 502

    content_type = upstream.headers.get('Content-Type', 'multipart/x-mixed-replace; boundary=--BoundaryString')

    @stream_with_context
    def generate():
        try:
            for chunk in upstream.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        finally:
            upstream.close()

    response = Response(generate(), mimetype=content_type)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Connection'] = 'close'
    return response


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _ratio_to_point(ratio_x: float, ratio_y: float, width: float, height: float):
    x = int(round(_clamp_ratio(ratio_x) * width))
    y = int(round(_clamp_ratio(ratio_y) * height))
    return x, y


@app.route('/api/devices/<device_id>/control/tap', methods=['POST'])
def control_tap(device_id):
    device = device_manager.get_device(device_id)
    if not device or device.platform != 'iOS':
        return jsonify({'success': False, 'error': 'Tap control only supports iOS devices'}), 400
    data = request.get_json(silent=True) or {}
    if 'x_ratio' not in data or 'y_ratio' not in data:
        return jsonify({'success': False, 'error': 'x_ratio and y_ratio are required'}), 400
    wda_url = device_manager.get_wda_url(device_id)
    if not wda_url:
        return jsonify({'success': False, 'error': 'WDA not available'}), 500
    import requests
    session_resp = requests.post(f"{wda_url}/session", json={"capabilities": {}}, timeout=15)
    session_data = session_resp.json() if session_resp.status_code in (200, 201) else {}
    session_id = session_data.get("sessionId") or session_data.get("value", {}).get("sessionId")
    if not session_id:
        return jsonify({'success': False, 'error': 'Failed to create WDA session'}), 500
    size_resp = requests.get(f"{wda_url}/session/{session_id}/window/size", timeout=15)
    size = size_resp.json().get("value", {}) if size_resp.status_code == 200 else {}
    width = float(size.get("width", 0))
    height = float(size.get("height", 0))
    if width <= 0 or height <= 0:
        return jsonify({'success': False, 'error': 'Failed to get screen size'}), 500
    x, y = _ratio_to_point(data['x_ratio'], data['y_ratio'], width, height)
    payload = {"actions": [{"type": "pointer", "id": "finger1", "parameters": {"pointerType": "touch"}, "actions": [{"type": "pointerMove", "duration": 0, "x": x, "y": y}, {"type": "pointerDown", "button": 0}, {"type": "pause", "duration": 0}, {"type": "pointerUp", "button": 0}]}]}
    action_resp = requests.post(f"{wda_url}/session/{session_id}/actions", json=payload, timeout=20)
    if action_resp.status_code not in (200, 201):
        return jsonify({'success': False, 'error': f'WDA tap failed: {action_resp.text[:200]}'}), 502
    return jsonify({'success': True, 'x': x, 'y': y})


@app.route('/api/devices/<device_id>/control/swipe', methods=['POST'])
def control_swipe(device_id):
    device = device_manager.get_device(device_id)
    if not device or device.platform != 'iOS':
        return jsonify({'success': False, 'error': 'Swipe control only supports iOS devices'}), 400
    data = request.get_json(silent=True) or {}
    required = ('start_x_ratio', 'start_y_ratio', 'end_x_ratio', 'end_y_ratio')
    if any(field not in data for field in required):
        return jsonify({'success': False, 'error': 'start/end ratio fields are required'}), 400
    duration_ms = int(data.get('duration_ms', 350))
    duration_sec = max(0.1, min(duration_ms / 1000.0, 3.0))
    wda_url = device_manager.get_wda_url(device_id)
    if not wda_url:
        return jsonify({'success': False, 'error': 'WDA not available'}), 500
    import requests
    session_resp = requests.post(f"{wda_url}/session", json={"capabilities": {}}, timeout=15)
    session_data = session_resp.json() if session_resp.status_code in (200, 201) else {}
    session_id = session_data.get("sessionId") or session_data.get("value", {}).get("sessionId")
    if not session_id:
        return jsonify({'success': False, 'error': 'Failed to create WDA session'}), 500
    size_resp = requests.get(f"{wda_url}/session/{session_id}/window/size", timeout=15)
    size = size_resp.json().get("value", {}) if size_resp.status_code == 200 else {}
    width = float(size.get("width", 0))
    height = float(size.get("height", 0))
    if width <= 0 or height <= 0:
        return jsonify({'success': False, 'error': 'Failed to get screen size'}), 500
    from_x, from_y = _ratio_to_point(data['start_x_ratio'], data['start_y_ratio'], width, height)
    to_x, to_y = _ratio_to_point(data['end_x_ratio'], data['end_y_ratio'], width, height)
    payload = {"fromX": from_x, "fromY": from_y, "toX": to_x, "toY": to_y, "duration": duration_sec}
    swipe_resp = requests.post(f"{wda_url}/session/{session_id}/wda/dragfromtoforduration", json=payload, timeout=20)
    if swipe_resp.status_code not in (200, 201):
        return jsonify({'success': False, 'error': f'WDA swipe failed: {swipe_resp.text[:200]}'}), 502
    return jsonify({'success': True, 'from': {'x': from_x, 'y': from_y}, 'to': {'x': to_x, 'y': to_y}})


@app.route('/api/devices/<device_id>/control/wake', methods=['POST'])
def control_wake(device_id):
    device = device_manager.get_device(device_id)
    if not device or device.platform != 'iOS':
        return jsonify({'success': False, 'error': 'Wake control only supports iOS devices'}), 400
    wda_url = device_manager.get_wda_url(device_id)
    if not wda_url:
        return jsonify({'success': False, 'error': 'WDA not available'}), 500
    import requests
    try:
        requests.post(f"{wda_url}/wda/pressButton", json={"name": "home"}, timeout=5)
    except Exception:
        pass
    return jsonify({'success': True})


@app.route('/api/devices/<device_id>/control/home', methods=['POST'])
def control_home(device_id):
    device = device_manager.get_device(device_id)
    if not device or device.platform != 'iOS':
        return jsonify({'success': False, 'error': 'Home control only supports iOS devices'}), 400
    wda_url = device_manager.get_wda_url(device_id)
    if not wda_url:
        return jsonify({'success': False, 'error': 'WDA not available'}), 500
    import requests
    resp = requests.post(f"{wda_url}/wda/homescreen", timeout=5)
    if resp.status_code not in (200, 201):
        return jsonify({'success': False, 'error': f'WDA home failed: {resp.text[:200]}'}), 502
    return jsonify({'success': True})


def create_agent_for_device(device_id: str):
    device = device_manager.get_device(device_id)
    if not device:
        raise ValueError(f"Device {device_id} not found")

    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    else:
        config_data = {'apiKey': Config.MODEL_API_KEY, 'modelType': 'glm-4', 'baseUrl': Config.MODEL_BASE_URL}

    model_config = ModelConfig(
        base_url=config_data.get('baseUrl', Config.MODEL_BASE_URL),
        api_key=config_data.get('apiKey', Config.MODEL_API_KEY),
        model_name=config_data.get('modelType', 'autoglm-phone')
    )

    if device.platform == 'iOS':
        if not device.local_port:
            device_manager.start_iproxy(device_id)
        wda_url = device_manager.get_wda_url(device_id)
        if not wda_url:
            raise ValueError(f"WDA not available for device {device_id}")
        agent_config = IOSAgentConfig(wda_url=wda_url, lang=Config.DEFAULT_LANG)
        return IOSPhoneAgent(model_config=model_config, agent_config=agent_config)
    elif device.platform == 'Android':
        if not ANDROID_SUPPORT:
            raise ValueError("Android Agent is not available.")
        agent_config = AndroidAgentConfig(serial_number=device_id, lang=Config.DEFAULT_LANG)
        return AndroidPhoneAgent(model_config=model_config, agent_config=agent_config)
    else:
        raise ValueError(f"Unsupported platform: {device.platform}")

@app.route('/run', methods=['POST'])
def run_task():
    task_desc = request.json.get('task')
    device_id = request.json.get('device_id')
    if not task_desc:
        return jsonify({"error": "No task provided"}), 400
    if not device_id:
        return jsonify({"error": "No device_id provided"}), 400
    
    # Save to database
    new_task = TaskHistory(task_description=task_desc, status='running', device_id=device_id)
    db.session.add(new_task)
    db.session.commit()
    task_id = new_task.id
    
    def target(tid, t_desc, dev_id):
        with app.app_context():
            import io
            import sys
            
            # 创建一个空的输出流，完全屏蔽 Agent 的详细输出
            class SilentOutput:
                def write(self, message):
                    pass
                def flush(self):
                    pass
            
            original_stdout = sys.stdout
            
            try:
                print(f"[Task {tid}] Starting task on device {dev_id}: {t_desc}")
                log_queue.put(f"📝 开始执行任务: {t_desc}")
                log_queue.put(f"📱 目标设备: {dev_id}")
                
                agent = create_agent_for_device(dev_id)
                print(f"[Task {tid}] Agent initialized for {dev_id}")
                log_queue.put("🤖 AI 正在分析任务并执行中，请稍候...")
                
                # 完全屏蔽 Agent 的输出，避免逐字显示
                sys.stdout = SilentOutput()
                
                result = agent.run(t_desc)
                
                # 恢复原始 stdout
                sys.stdout = original_stdout
                
                print(f"[Task {tid}] Task completed: {result}")
                log_queue.put("✅ 任务执行完成")
                log_queue.put(f"📊 执行结果: {result[:300]}")
                
                task = TaskHistory.query.get(tid)
                task.status = 'completed'
                task.result_message = result
                task.finished_at = datetime.utcnow()
                db.session.commit()
                log_queue.put("__END__")
            except Exception as e:
                import traceback
                sys.stdout = original_stdout
                error_detail = traceback.format_exc()
                print(f"[Task {tid}] Error: {error_detail}")
                log_queue.put(f"❌ 任务执行失败: {str(e)}")
                
                task = TaskHistory.query.get(tid)
                task.status = 'failed'
                task.result_message = f"错误: {str(e)}\n{error_detail[:500]}"
                task.finished_at = datetime.utcnow()
                db.session.commit()
                log_queue.put("__END__")

    threading.Thread(target=target, args=(task_id, task_desc, device_id)).start()
    return jsonify({"status": "started", "task_id": task_id})

@app.route('/logs')
def logs():
    def generate():
        while True:
            try:
                # 设置超时，避免永久阻塞
                message = log_queue.get(timeout=60)
                if message == "__END__":
                    yield "data: END\n\n"
                    break
                yield f"data: {message}\n\n"
            except:
                # 超时或其他错误，结束流
                yield "data: END\n\n"
                break
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

# ==================== 测试用例管理 API ====================

@app.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """获取所有测试用例"""
    category = request.args.get('category')
    if category:
        cases = TestCase.query.filter_by(category=category, is_active=True).all()
    else:
        cases = TestCase.query.filter_by(is_active=True).all()
    return jsonify([case.to_dict() for case in cases])

@app.route('/api/test-cases', methods=['POST'])
def create_test_case():
    """创建新测试用例"""
    data = request.json
    new_case = TestCase(
        name=data.get('name'),
        description=data.get('description', ''),
        instruction=data.get('instruction'),
        category=data.get('category', 'general')
    )
    db.session.add(new_case)
    db.session.commit()
    return jsonify(new_case.to_dict()), 201

@app.route('/api/test-cases/<int:case_id>', methods=['PUT'])
def update_test_case(case_id):
    """更新测试用例"""
    case = TestCase.query.get_or_404(case_id)
    data = request.json
    
    if 'name' in data:
        case.name = data['name']
    if 'description' in data:
        case.description = data['description']
    if 'instruction' in data:
        case.instruction = data['instruction']
    if 'category' in data:
        case.category = data['category']
    if 'is_active' in data:
        case.is_active = data['is_active']
    
    case.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(case.to_dict())

@app.route('/api/test-cases/<int:case_id>', methods=['DELETE'])
def delete_test_case(case_id):
    """删除测试用例（软删除）"""
    case = TestCase.query.get_or_404(case_id)
    case.is_active = False
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/test-cases/init', methods=['POST'])
def init_test_cases():
    """初始化默认测试用例"""
    default_cases = [
        {
            'name': '打开设置',
            'description': '测试打开系统设置应用',
            'instruction': '打开设置',
            'category': 'system'
        },
        {
            'name': '打开微信',
            'description': '测试打开微信应用',
            'instruction': '打开微信',
            'category': 'app'
        },
        {
            'name': '查看通讯录',
            'description': '打开微信并进入通讯录',
            'instruction': '打开微信，点击通讯录',
            'category': 'app'
        },
        {
            'name': '打开相机',
            'description': '测试打开相机应用',
            'instruction': '打开相机',
            'category': 'system'
        },
        {
            'name': '打开照片',
            'description': '测试打开照片应用',
            'instruction': '打开照片',
            'category': 'system'
        },
        {
            'name': '调整音量',
            'description': '打开设置并调整音量',
            'instruction': '打开设置，进入声音与触感，调整铃声音量',
            'category': 'system'
        },
        {
            'name': '查看WiFi设置',
            'description': '打开WiFi设置页面',
            'instruction': '打开设置，点击无线局域网',
            'category': 'system'
        },
        {
            'name': '打开Safari',
            'description': '测试打开Safari浏览器',
            'instruction': '打开Safari',
            'category': 'app'
        },
        {
            'name': '查看电池信息',
            'description': '打开设置并查看电池信息',
            'instruction': '打开设置，点击电池',
            'category': 'system'
        },
        {
            'name': '打开App Store',
            'description': '测试打开App Store',
            'instruction': '打开App Store',
            'category': 'app'
        }
    ]
    
    # 检查是否已经初始化过
    existing_count = TestCase.query.count()
    if existing_count > 0:
        return jsonify({'message': '测试用例已存在', 'count': existing_count})
    
    # 批量创建测试用例
    for case_data in default_cases:
        case = TestCase(**case_data)
        db.session.add(case)
    
    db.session.commit()
    return jsonify({'message': '成功创建默认测试用例', 'count': len(default_cases)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
