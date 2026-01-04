import os

class Config:
    # AI Model Configuration
    MODEL_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
    MODEL_API_KEY = "78fd6426a1124a0d989292c028230351.0rpceEypavcHTFWQ"
    MODEL_NAME = "autoglm-phone"
    
    # Agent Configuration
    WDA_URL = "http://localhost:8100"
    DEFAULT_LANG = "cn"
    
    # Server Configuration
    PORT = 5001
    HOST = '0.0.0.0'
    DEBUG = False
    
    # Database Configuration
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database", "phone_agent.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
