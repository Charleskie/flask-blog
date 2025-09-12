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
    like_count = db.Column(db.Integer, default=0)  # 点赞数
    favorite_count = db.Column(db.Integer, default=0)  # 收藏数
    comment_count = db.Column(db.Integer, default=0)  # 评论数
    average_rating = db.Column(db.Float, default=0.0)  # 平均评分
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关联关系
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def generate_slug(self):
        """生成URL友好的标题"""
        if not self.title:
            return f"post-{self.id or 'new'}"
        
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        
        # 如果生成的slug为空，使用默认值
        if not slug:
            slug = f"post-{self.id or 'new'}"
        
        return slug
    
    @property
    def safe_slug(self):
        """获取安全的slug，如果没有则生成一个"""
        if self.slug:
            return self.slug
        return self.generate_slug()
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return [] 