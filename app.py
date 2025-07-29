#!/usr/bin/env python3
"""
个人网站应用入口
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///personal_website.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'

# 导入模型
from app.models.user import User
from app.models.post import Post
from app.models.project import Project
from app.models.message import Message

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 注册蓝图
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')

# 注册过滤器
from app.utils.filters import nl2br
app.jinja_env.filters['nl2br'] = nl2br

if __name__ == '__main__':
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
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
    app.run(debug=True, host='0.0.0.0', port=5000)