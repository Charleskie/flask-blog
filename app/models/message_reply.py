from .user import db
from datetime import datetime

class MessageReply(db.Model):
    """消息回复模型"""
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    reply_content = db.Column(db.Text, nullable=False)
    reply_type = db.Column(db.String(20), default='admin')  # admin, user
    sender_name = db.Column(db.String(100), nullable=True)  # 发送者姓名
    sender_email = db.Column(db.String(120), nullable=True)  # 发送者邮箱
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_sent = db.Column(db.Boolean, default=False)  # 是否已发送邮件
    sent_at = db.Column(db.DateTime, nullable=True)  # 发送时间
    
    # 关联关系
    message = db.relationship('Message', backref=db.backref('replies', lazy=True, order_by='MessageReply.created_at.desc()'))
    
    def __repr__(self):
        return f'<MessageReply {self.id}>'
    
    def mark_as_sent(self):
        """标记为已发送"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
    
    @classmethod
    def create_reply(cls, message_id, reply_content, reply_type='admin', sender_name=None, sender_email=None):
        """创建回复记录"""
        reply = cls(
            message_id=message_id,
            reply_content=reply_content,
            reply_type=reply_type,
            sender_name=sender_name,
            sender_email=sender_email
        )
        return reply
