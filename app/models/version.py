from app.models.user import db
from datetime import datetime

class Version(db.Model):
    """版本更新记录模型"""
    __tablename__ = 'versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_number = db.Column(db.String(20), nullable=False, unique=True)  # 版本号，如 v1.0.0
    title = db.Column(db.String(200), nullable=False)  # 版本标题
    description = db.Column(db.Text, nullable=False)  # 版本描述
    release_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 发布日期
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    is_active = db.Column(db.Boolean, default=True)  # 是否激活
    
    def __repr__(self):
        return f'<Version {self.version_number}: {self.title}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'version_number': self.version_number,
            'title': self.title,
            'description': self.description,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
