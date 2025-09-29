from .user import db
from datetime import datetime

class Message(db.Model):
    """消息模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread')  # unread, read, replied, in_conversation, archived
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
        if self.status == 'unread' or self.status == 'read':
            self.status = 'replied'
        else:
            self.status = 'in_conversation'  # 进入对话状态
        self.replied_at = datetime.utcnow()
    
    def is_unread(self):
        """检查是否未读"""
        return self.status == 'unread'
    
    def is_replied(self):
        """检查是否已回复"""
        return self.status == 'replied'
    
    @classmethod
    def create_message_notification(cls, message):
        """创建新消息通知"""
        from .notification import Notification
        
        # 获取管理员用户（这里假设ID为1的用户是管理员）
        admin_user = db.session.query(db.Model.metadata.tables['user']).filter_by(id=1).first()
        if not admin_user:
            return None
            
        notification = Notification(
            user_id=1,  # 管理员用户ID
            type='message',
            title=f'新消息：{message.subject}',
            content=f'来自 {message.name} 的消息：{message.message[:100]}{"..." if len(message.message) > 100 else ""}',
            related_id=message.id,
            related_type='message',
            related_url=f'/admin/messages/{message.id}',
            sender_name=message.name
        )
        return notification 