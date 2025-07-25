from .user import db
from datetime import datetime
import re

class Post(db.Model):
    """文章模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)  # 文章摘要
    slug = db.Column(db.String(200), unique=True, nullable=True)  # URL友好的标题
    status = db.Column(db.String(20), default='draft')  # draft, published
    category = db.Column(db.String(50), nullable=True)  # 分类
    tags = db.Column(db.String(200), nullable=True)  # 标签，用逗号分隔
    featured_image = db.Column(db.String(500), nullable=True)  # 特色图片
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关联关系
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def generate_slug(self):
        """生成URL友好的标题"""
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return slug
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return [] 