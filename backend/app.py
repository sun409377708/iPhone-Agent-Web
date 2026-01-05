import os
import sys
import threading
import queue
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from .models import db, TaskHistory, TestCase
from .config import Config

# Add Open-AutoGLM directory to path to import phone_agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Open-AutoGLM')))

from phone_agent.agent_ios import IOSAgentConfig, IOSPhoneAgent
from phone_agent.model import ModelConfig

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
    """Get connected devices"""
    devices = []
    try:
        agent_instance = get_agent()
        if agent_instance and hasattr(agent_instance, 'device_info'):
            device_info = agent_instance.device_info()
            devices.append({
                'id': device_info.get('udid', 'unknown'),
                'name': device_info.get('name', 'iOS Device'),
                'platform': 'iOS',
                'model': device_info.get('model', 'Unknown'),
                'version': device_info.get('version', 'Unknown'),
                'status': 'online'
            })
        else:
            devices.append({
                'id': 'ios-device-1',
                'name': 'iPhone',
                'platform': 'iOS',
                'model': 'iPhone',
                'version': 'Unknown',
                'status': 'online'
            })
    except Exception as e:
        print(f"Error getting device info: {e}")
        devices.append({
            'id': 'ios-device-1',
            'name': 'iPhone',
            'platform': 'iOS',
            'model': 'iPhone',
            'version': 'Unknown',
            'status': 'online'
        })
    
    return jsonify({'devices': devices})

@app.route('/api/history', methods=['GET'])
def get_history():
    history = TaskHistory.query.order_by(TaskHistory.created_at.desc()).limit(20).all()
    return jsonify([task.to_dict() for task in history])

@app.route('/api/screenshot', methods=['GET'])
def get_screenshot():
    """获取设备截图"""
    try:
        import requests
        import base64
        from io import BytesIO
        from PIL import Image
        
        # 通过 WDA 获取截图 (WDA 返回的是 JSON 格式，包含 base64 编码的图片)
        response = requests.get(f"{Config.WDA_URL}/screenshot", timeout=10)
        if response.status_code == 200:
            # WDA 返回的是 JSON: {"value": "base64_encoded_png", "sessionId": "..."}
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

@app.route('/run', methods=['POST'])
def run_task():
    task_desc = request.json.get('task')
    if not task_desc:
        return jsonify({"error": "No task provided"}), 400
    
    # Save to database
    new_task = TaskHistory(task_description=task_desc, status='running')
    db.session.add(new_task)
    db.session.commit()
    task_id = new_task.id
    
    def target(tid, t_desc):
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
                print(f"[Task {tid}] Starting task: {t_desc}")
                log_queue.put(f"📝 开始执行任务: {t_desc}")
                
                agent = get_agent()
                print(f"[Task {tid}] Agent initialized")
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

    threading.Thread(target=target, args=(task_id, task_desc)).start()
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
