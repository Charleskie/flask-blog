from datetime import datetime
from app.models.user import db

class UserInteraction(db.Model):
    """用户互动模型 - 统一管理点赞、收藏、评分"""
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, nullable=False)  # 文章或项目ID
    type = db.Column(db.Integer, nullable=False)  # 1-博客；2-项目
    like = db.Column(db.Integer, default=0)  # 1-点赞；0-没有点赞
    favorite = db.Column(db.Integer, default=0)  # 1-收藏；0-没有收藏
    rating = db.Column(db.Integer, default=0)  # 0~5分，0表示没有评分
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 确保每个用户对同一内容只有一条互动记录
    __table_args__ = (
        db.UniqueConstraint('user_id', 'content_id', 'type', name='unique_user_content_interaction'),
    )
    
    def __repr__(self):
        return f'<UserInteraction {self.id}>'

# 保留原有的Like和Favorite模型以保持向后兼容
class Like(db.Model):
    """点赞模型 - 已废弃，保留用于数据迁移"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保每个用户对同一内容只能点赞一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
        db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_like'),
    )
    
    def __repr__(self):
        return f'<Like {self.id}>'

class Favorite(db.Model):
    """收藏模型 - 已废弃，保留用于数据迁移"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保每个用户对同一内容只能收藏一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_favorite'),
        db.UniqueConstraint('user_id', 'project_id', name='unique_user_project_favorite'),
    )
    
    def __repr__(self):
        return f'<Favorite {self.id}>'

class Comment(db.Model):
    """评论模型 - 评分功能已移至UserInteraction模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    project = db.relationship('Project', backref=db.backref('comments', lazy='dynamic'))
    
    # 回复关系
    replies = db.relationship('CommentReply', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class CommentReply(db.Model):
    """评论回复模型"""
    __tablename__ = 'comment_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('comment_replies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CommentReply {self.id}>'
