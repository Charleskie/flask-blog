from .user import db
from datetime import datetime

class Project(db.Model):
    """项目模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(300), nullable=True)  # 简短描述
    image_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))  # 演示链接
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    category = db.Column(db.String(50), nullable=True)  # 项目分类
    tags = db.Column(db.String(200), nullable=True)  # 技术标签
    technologies = db.Column(db.Text, nullable=True)  # 使用的技术栈
    features = db.Column(db.Text, nullable=True)  # 主要功能特性
    challenges = db.Column(db.Text, nullable=True)  # 遇到的挑战
    lessons_learned = db.Column(db.Text, nullable=True)  # 学到的经验
    view_count = db.Column(db.Integer, default=0)  # 浏览次数
    like_count = db.Column(db.Integer, default=0)  # 点赞数
    favorite_count = db.Column(db.Integer, default=0)  # 收藏数
    comment_count = db.Column(db.Integer, default=0)  # 评论数
    average_rating = db.Column(db.Float, default=0.0)  # 平均评分
    featured = db.Column(db.Boolean, default=False)  # 是否推荐项目
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
    def get_technologies_list(self):
        """获取技术栈列表"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_features_list(self):
        """获取功能特性列表"""
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return [] 