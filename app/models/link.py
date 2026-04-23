from .user import db
from datetime import datetime

class Link(db.Model):
    """友链模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 网站名称
    url = db.Column(db.String(500), nullable=False)  # 网站链接
    description = db.Column(db.String(300), nullable=True)  # 网站描述
    avatar_url = db.Column(db.String(500), nullable=True)  # 网站头像
    email = db.Column(db.String(100), nullable=True)  # 联系邮箱
    status = db.Column(db.String(20), default='active')  # active, pending, inactive
    featured = db.Column(db.Boolean, default=False)  # 是否推荐
    sort_order = db.Column(db.Integer, default=0)  # 排序权重
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Link {self.name}>'
    
    @staticmethod
    def get_active_links():
        """获取所有活跃的友链"""
        return Link.query.filter_by(status='active').order_by(Link.sort_order.desc(), Link.created_at.desc()).all()
    
    @staticmethod
    def get_featured_links():
        """获取推荐的友链"""
        return Link.query.filter_by(status='active', featured=True).order_by(Link.sort_order.desc(), Link.created_at.desc()).all()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'avatar_url': self.avatar_url,
            'email': self.email,
            'status': self.status,
            'featured': self.featured,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
