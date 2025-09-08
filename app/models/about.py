from .user import db
from datetime import datetime

class AboutContent(db.Model):
    """关于页面内容模型"""
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), nullable=False, unique=True)  # 内容区块标识
    title = db.Column(db.String(200), nullable=False)  # 区块标题
    content = db.Column(db.Text, nullable=False)  # 区块内容
    order = db.Column(db.Integer, default=0)  # 显示顺序
    is_active = db.Column(db.Boolean, default=True)  # 是否显示
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AboutContent {self.section}: {self.title}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'section': self.section,
            'title': self.title,
            'content': self.content,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AboutContact(db.Model):
    """关于页面联系方式模型"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # 平台名称
    icon = db.Column(db.String(50), nullable=False)  # 图标类名
    url = db.Column(db.String(500), nullable=True)  # 链接地址
    text = db.Column(db.String(200), nullable=False)  # 显示文本
    color = db.Column(db.String(20), default='primary')  # 图标颜色
    order = db.Column(db.Integer, default=0)  # 显示顺序
    is_active = db.Column(db.Boolean, default=True)  # 是否显示
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AboutContact {self.platform}: {self.text}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'platform': self.platform,
            'icon': self.icon,
            'url': self.url,
            'text': self.text,
            'color': self.color,
            'order': self.order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
