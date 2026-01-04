from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TaskHistory(db.Model):
    __tablename__ = 'task_history'
    
    id = db.Column(db.Integer, primary_key=True)
    task_description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    result_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task_description': self.task_description,
            'status': self.status,
            'result_message': self.result_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None
        }
