#!/usr/bin/env python3
"""
个人网站启动脚本
"""

from app import create_app
from app.models.user import db
from app.models import User, Post, Message

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表
        db.create_all()

    print("🚀 启动个人网站服务器...")
    print("📱 访问地址: http://localhost:8000")
    print("🔧 管理后台: http://localhost:8000/admin")
    print("⏹️  按 Ctrl+C 停止服务器")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
