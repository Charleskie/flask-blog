from datetime import datetime
from .user import db


class Skill(db.Model):
    """技能模型"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='技能名称')
    icon = db.Column(db.String(200), nullable=True, comment='技能图标（CSS类名或图标URL）')
    proficiency = db.Column(db.Integer, nullable=False, default=0, comment='技能熟练度（0-100）')
    category = db.Column(db.String(50), nullable=True, comment='技能分类（如：前端、后端、数据库等）')
    description = db.Column(db.Text, nullable=True, comment='技能描述')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    sort_order = db.Column(db.Integer, default=0, comment='排序顺序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<Skill {self.name}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'proficiency': self.proficiency,
            'category': self.category,
            'description': self.description,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_skills(cls, category=None):
        """获取启用的技能列表"""
        query = cls.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(cls.sort_order.asc(), cls.name.asc()).all()
    
    @classmethod
    def get_skills_by_category(cls):
        """按分类获取技能"""
        skills = cls.get_active_skills()
        categories = {}
        for skill in skills:
            category = skill.category or '其他'
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        return categories
