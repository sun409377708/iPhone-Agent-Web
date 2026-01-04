import os
import sys
import threading
import queue
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from .models import db, TaskHistory
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
CORS(app)

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

sys.stdout = StreamLogger(log_queue)

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

@app.route('/api/history', methods=['GET'])
def get_history():
    history = TaskHistory.query.order_by(TaskHistory.created_at.desc()).limit(20).all()
    return jsonify([task.to_dict() for task in history])

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
            try:
                result = get_agent().run(t_desc)
                task = TaskHistory.query.get(tid)
                task.status = 'completed'
                task.result_message = result
                task.finished_at = datetime.utcnow()
                db.session.commit()
                log_queue.put("__END__")
            except Exception as e:
                task = TaskHistory.query.get(tid)
                task.status = 'failed'
                task.result_message = str(e)
                task.finished_at = datetime.utcnow()
                db.session.commit()
                log_queue.put(f"Error: {str(e)}")
                log_queue.put("__END__")

    threading.Thread(target=target, args=(task_id, task_desc)).start()
    return jsonify({"status": "started", "task_id": task_id})

@app.route('/logs')
def logs():
    def generate():
        while True:
            message = log_queue.get()
            if message == "__END__":
                yield "data: END\n\n"
                break
            yield f"data: {message}\n\n"
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
