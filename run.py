import os
import sys

# Add the current directory to sys.path to allow importing from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    # You can configure port and host here
    print("🚀 Starting Phone Agent Web Server...")
    print("🔗 Local Access: http://127.0.0.1:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
