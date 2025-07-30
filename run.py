#!/usr/bin/env python3
"""
个人网站启动脚本
"""

from app import create_app
from app.models.user import db
from app.models import User, Post, Project, Message

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            from datetime import datetime
            
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                created_at=datetime.utcnow(),
                nickname='管理员',
                avatar='',
                bio='网站管理员，负责网站的管理和维护',
                website='',
                location='中国',
                company='个人网站',
                job_title='管理员',
                phone='',
                theme='light',
                language='zh-CN',
                timezone='Asia/Shanghai',
                two_factor_enabled=False,
                login_notifications=True,
                session_timeout=30,
                last_login=None,
                last_login_ip=None,
                profile_public=True,
                show_email=False,
                show_phone=False
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员用户已创建：用户名 admin，密码 admin123")
        else:
            print("✅ 管理员用户已存在")
    
    print("🚀 启动个人网站服务器...")
    print("📱 访问地址: http://localhost:8000")
    print("🔧 管理后台: http://localhost:8000/admin")
    print("⏹️  按 Ctrl+C 停止服务器")
    
    app.run(debug=True, host='0.0.0.0', port=8000)