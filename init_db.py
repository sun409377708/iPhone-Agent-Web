#!/usr/bin/env python3
"""初始化数据库，创建测试用例表"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app, db

with app.app_context():
    # 创建所有表
    db.create_all()
    print("✅ 数据库表创建成功！")
    print("📊 可用的表：")
    print("  - task_history")
    print("  - test_cases")
