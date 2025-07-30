from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 个人信息
    nickname = db.Column(db.String(80))
    avatar = db.Column(db.String(200))  # 头像URL
    bio = db.Column(db.Text)  # 个人简介
    website = db.Column(db.String(200))  # 个人网站
    location = db.Column(db.String(100))  # 所在地
    company = db.Column(db.String(100))  # 公司
    job_title = db.Column(db.String(100))  # 职位
    phone = db.Column(db.String(20))  # 电话
    
    # 主题设置
    theme = db.Column(db.String(20), default='light')  # light, dark, auto
    language = db.Column(db.String(10), default='zh-CN')  # zh-CN, en-US
    timezone = db.Column(db.String(50), default='Asia/Shanghai')
    
    # 安全设置
    two_factor_enabled = db.Column(db.Boolean, default=False)  # 双因素认证
    login_notifications = db.Column(db.Boolean, default=True)  # 登录通知
    session_timeout = db.Column(db.Integer, default=30)  # 会话超时时间(分钟)
    last_login = db.Column(db.DateTime)  # 最后登录时间
    last_login_ip = db.Column(db.String(45))  # 最后登录IP
    
    # 隐私设置
    profile_public = db.Column(db.Boolean, default=True)  # 个人资料是否公开
    show_email = db.Column(db.Boolean, default=False)  # 是否显示邮箱
    show_phone = db.Column(db.Boolean, default=False)  # 是否显示电话

    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_display_name(self):
        """获取显示名称"""
        return self.nickname or self.username
    
    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            return self.avatar
        # 默认头像，使用Gravatar或本地默认头像
        return f"https://www.gravatar.com/avatar/{hash(self.email)}?d=identicon&s=200"
    
    def update_last_login(self, ip_address):
        """更新最后登录信息"""
        self.last_login = datetime.utcnow()
        self.last_login_ip = ip_address
        db.session.commit() 