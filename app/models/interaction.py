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
    
    # 关系
    user = db.relationship('User', backref=db.backref('interactions', lazy=True))
    
    def __repr__(self):
        return f'<UserInteraction {self.id}>'

class CommentLike(db.Model):
    """评论点赞模型"""
    __tablename__ = 'comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 确保每个用户对同一评论只能点赞一次
    __table_args__ = (
        db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_like'),
    )
    
    def __repr__(self):
        return f'<CommentLike {self.id}>'

class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    like_count = db.Column(db.Integer, default=0)  # 点赞数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
    post = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))
    project = db.relationship('Project', backref=db.backref('comments', lazy='dynamic'))
    
    # 回复关系
    replies = db.relationship('CommentReply', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    # 点赞关系
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def is_liked_by(self, user_id):
        """检查用户是否已点赞此评论"""
        return self.likes.filter_by(user_id=user_id).first() is not None
    
    def toggle_like(self, user_id):
        """切换点赞状态"""
        like = self.likes.filter_by(user_id=user_id).first()
        if like:
            # 取消点赞
            db.session.delete(like)
            self.like_count = max(0, self.like_count - 1)
            return False
        else:
            # 添加点赞
            like = CommentLike(user_id=user_id, comment_id=self.id)
            db.session.add(like)
            self.like_count += 1
            return True

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