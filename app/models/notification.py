from datetime import datetime
from app.models.user import db


class Notification(db.Model):
    """系统消息通知模型"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # comment, reply, like, favorite, rating
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # 关联数据 - 用于跳转
    related_id = db.Column(db.Integer, nullable=True)  # 关联的评论/文章/项目ID
    related_type = db.Column(db.String(20), nullable=True)  # post, project, comment
    related_url = db.Column(db.String(500), nullable=True)  # 跳转URL
    
    # 发送者信息
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    sender_name = db.Column(db.String(100), nullable=True)
    
    # 关联关系
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('notifications', lazy='dynamic'))
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification {self.id}>'
    
    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'related_id': self.related_id,
            'related_type': self.related_type,
            'related_url': self.related_url,
            'sender_name': self.sender_name
        }
    
    @classmethod
    def create_comment_notification(cls, post_author_id, commenter_name, comment_content, post_id, post_title):
        """创建评论通知"""
        notification = cls(
            user_id=post_author_id,
            type='comment',
            title=f'{commenter_name} 评论了你的文章',
            content=f'"{comment_content[:100]}{"..." if len(comment_content) > 100 else ""}"',
            related_id=post_id,
            related_type='post',
            related_url=f'/blog/post/{post_id}',
            sender_name=commenter_name
        )
        return notification
    
    @classmethod
    def create_reply_notification(cls, comment_author_id, replier_name, reply_content, comment_id, post_id, post_title):
        """创建回复通知"""
        notification = cls(
            user_id=comment_author_id,
            type='reply',
            title=f'{replier_name} 回复了你的评论',
            content=f'"{reply_content[:100]}{"..." if len(reply_content) > 100 else ""}"',
            related_id=comment_id,
            related_type='comment',
            related_url=f'/blog/post/{post_id}#comment-{comment_id}',
            sender_name=replier_name
        )
        return notification
    
    @classmethod
    def create_like_notification(cls, content_author_id, liker_name, content_type, content_id, content_title):
        """创建点赞通知"""
        notification = cls(
            user_id=content_author_id,
            type='like',
            title=f'{liker_name} 点赞了你的{content_type}',
            content=f'"{content_title}"',
            related_id=content_id,
            related_type=content_type,
            related_url=f'/blog/post/{content_id}' if content_type == 'post' else f'/projects/{content_id}',
            sender_name=liker_name
        )
        return notification
    
    @classmethod
    def create_favorite_notification(cls, content_author_id, favoriter_name, content_type, content_id, content_title):
        """创建收藏通知"""
        notification = cls(
            user_id=content_author_id,
            type='favorite',
            title=f'{favoriter_name} 收藏了你的{content_type}',
            content=f'"{content_title}"',
            related_id=content_id,
            related_type=content_type,
            related_url=f'/blog/post/{content_id}' if content_type == 'post' else f'/projects/{content_id}',
            sender_name=favoriter_name
        )
        return notification
    
    @classmethod
    def create_rating_notification(cls, content_author_id, rater_name, rating, content_type, content_id, content_title):
        """创建评分通知"""
        notification = cls(
            user_id=content_author_id,
            type='rating',
            title=f'{rater_name} 给你的{content_type}打了{rating}分',
            content=f'"{content_title}"',
            related_id=content_id,
            related_type=content_type,
            related_url=f'/blog/post/{content_id}' if content_type == 'post' else f'/projects/{content_id}',
            sender_name=rater_name
        )
        return notification
    
    @classmethod
    def create_message_reply_notification(cls, message_author_id, admin_name, message_subject, message_id):
        """创建私信回复通知"""
        notification = cls(
            user_id=message_author_id,
            type='message_reply',
            title=f'{admin_name} 回复了你的私信',
            content=f'"{message_subject}"',
            related_id=message_id,
            related_type='message',
            related_url=f'/contact',  # 跳转到联系页面
            sender_name=admin_name
        )
        return notification