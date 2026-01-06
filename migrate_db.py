#!/usr/bin/env python3
"""数据库迁移脚本：添加 device_id 字段到 task_history 表"""

import os
import sys
import sqlite3

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """执行数据库迁移"""
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'phone_agent.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先运行 init_db.py 创建数据库")
        return False
    
    print(f"📊 连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查 device_id 列是否已存在
        cursor.execute("PRAGMA table_info(task_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'device_id' in columns:
            print("✅ device_id 字段已存在，无需迁移")
            return True
        
        # 添加 device_id 列
        print("🔧 添加 device_id 字段到 task_history 表...")
        cursor.execute("""
            ALTER TABLE task_history 
            ADD COLUMN device_id VARCHAR(200)
        """)
        
        conn.commit()
        print("✅ 数据库迁移成功！")
        print("📝 已添加字段: device_id (VARCHAR(200))")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("  数据库迁移工具")
    print("=" * 50)
    print()
    
    success = migrate_database()
    
    print()
    if success:
        print("🎉 迁移完成！")
    else:
        print("⚠️  迁移失败，请检查错误信息")
        sys.exit(1)
