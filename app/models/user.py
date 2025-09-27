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
    
    
    # 安全设置
    two_factor_enabled = db.Column(db.Boolean, default=False)  # 双因素认证
    login_notifications = db.Column(db.Boolean, default=True)  # 登录通知
    session_timeout = db.Column(db.Integer, default=30)  # 会话超时时间(分钟)
    last_login = db.Column(db.DateTime)  # 最后登录时间
    last_login_ip = db.Column(db.String(45))  # 最后登录IP
    
    # 密码重置相关
    reset_password_token = db.Column(db.String(100))  # 重置密码令牌
    reset_password_expires = db.Column(db.DateTime)  # 重置密码令牌过期时间
    
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
        # 使用本地默认头像，根据用户ID选择不同的默认头像
        default_avatar = f"/static/avatar/avatar{(self.id % 4) + 1}.png"
        return default_avatar
    
    def update_last_login(self, ip_address):
        """更新最后登录信息"""
        self.last_login = datetime.utcnow()
        self.last_login_ip = ip_address
        db.session.commit()
    
    def generate_reset_token(self):
        """生成重置密码令牌"""
        import secrets
        import hashlib
        from datetime import datetime, timedelta
        
        # 生成随机令牌
        token = secrets.token_urlsafe(32)
        # 对令牌进行哈希处理
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # 设置过期时间（24小时）
        expires = datetime.utcnow() + timedelta(hours=24)
        
        # 保存到数据库
        self.reset_password_token = token_hash
        self.reset_password_expires = expires
        db.session.commit()
        
        return token
    
    def verify_reset_token(self, token):
        """验证重置密码令牌"""
        import hashlib
        from datetime import datetime
        
        if not self.reset_password_token or not self.reset_password_expires:
            return False
        
        # 检查令牌是否过期
        if datetime.utcnow() > self.reset_password_expires:
            return False
        
        # 验证令牌
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash == self.reset_password_token
    
    def clear_reset_token(self):
        """清除重置密码令牌"""
        self.reset_password_token = None
        self.reset_password_expires = None
        db.session.commit()
    
    @staticmethod
    def verify_reset_token_static(token):
        """静态方法：通过令牌查找用户"""
        import hashlib
        from datetime import datetime
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user = User.query.filter_by(reset_password_token=token_hash).first()
        
        if not user or not user.reset_password_expires:
            return None
        
        # 检查令牌是否过期
        if datetime.utcnow() > user.reset_password_expires:
            return None
        
        return user 