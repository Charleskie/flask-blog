from .user import db
from datetime import datetime

class Message(db.Model):
    """消息模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread')  # unread, read, replied, archived
    ip_address = db.Column(db.String(45), nullable=True)  # 存储IP地址
    user_agent = db.Column(db.Text, nullable=True)  # 存储用户代理
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)  # 阅读时间
    replied_at = db.Column(db.DateTime, nullable=True)  # 回复时间

    def __repr__(self):
        return f'<Message {self.subject}>'
    
    def mark_as_read(self):
        """标记为已读"""
        self.status = 'read'
        self.read_at = datetime.utcnow()
    
    def mark_as_replied(self):
        """标记为已回复"""
        self.status = 'replied'
        self.replied_at = datetime.utcnow()
    
    def is_unread(self):
        """检查是否未读"""
        return self.status == 'unread'
    
    def is_replied(self):
        """检查是否已回复"""
        return self.status == 'replied' 