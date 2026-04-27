from .user import db
from datetime import datetime

class Message(db.Model):
    """消息模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unread')  # unread, read, replied, in_conversation, archived
    ip_address = db.Column(db.String(45), nullable=True)  # 存储IP地址
    user_agent = db.Column(db.Text, nullable=True)  # 存储用户代理
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)  # 阅读时间
    user_read_at = db.Column(db.DateTime, nullable=True)  # 用户侧最近阅读时间
    replied_at = db.Column(db.DateTime, nullable=True)  # 回复时间
    user_deleted_at = db.Column(db.DateTime, nullable=True)  # 用户侧删除时间
    admin_deleted_at = db.Column(db.DateTime, nullable=True)  # 管理员侧删除时间

    def __repr__(self):
        return f'<Message {self.subject}>'
    
    def mark_as_read(self):
        """标记为已读"""
        self.mark_as_read_by_admin()

    def mark_as_read_by_admin(self):
        """标记管理员侧已读。"""
        self.read_at = datetime.utcnow()
        if self.status == 'unread':
            self.status = 'read'

    def mark_as_read_by_user(self):
        """标记用户侧已读。"""
        self.user_read_at = datetime.utcnow()
    
    def mark_as_replied(self):
        """标记为已回复"""
        if self.status == 'unread' or self.status == 'read':
            self.status = 'replied'
        else:
            self.status = 'in_conversation'  # 进入对话状态
        self.replied_at = datetime.utcnow()
    
    def is_unread(self):
        """检查是否未读"""
        return self.status == 'unread'
    
    def is_replied(self):
        """检查是否已回复"""
        return self.status == 'replied'

    @property
    def latest_reply(self):
        """按当前关系排序返回最新回复。"""
        return self.replies[0] if self.replies else None

    def latest_incoming_for_admin_at(self):
        """返回管理员侧最近一条需要关注的来信时间。"""
        latest_reply = self.latest_reply
        if latest_reply and latest_reply.reply_type == 'user':
            return latest_reply.created_at
        if latest_reply is None:
            return self.created_at
        return None

    def latest_incoming_for_user_at(self):
        """返回用户侧最近一条需要关注的管理员回复时间。"""
        latest_reply = self.latest_reply
        if latest_reply and latest_reply.reply_type == 'admin':
            return latest_reply.created_at
        return None

    def has_unread_for_admin(self):
        """管理员侧是否存在未读消息。"""
        latest_incoming = self.latest_incoming_for_admin_at()
        if latest_incoming is None:
            return False
        return self.read_at is None or self.read_at < latest_incoming

    def has_unread_for_user(self):
        """用户侧是否存在未读管理员回复。"""
        latest_incoming = self.latest_incoming_for_user_at()
        if latest_incoming is None:
            return False
        return self.user_read_at is None or self.user_read_at < latest_incoming

    @classmethod
    def visible_to_user_query(cls, email):
        """返回用户侧仍可见的会话查询。"""
        return cls.query.filter(
            cls.email == email,
            cls.user_deleted_at.is_(None)
        )

    @classmethod
    def visible_to_admin_query(cls):
        """返回管理员侧仍可见的会话查询。"""
        return cls.query.filter(cls.admin_deleted_at.is_(None))

    def hide_for_user(self):
        """仅在用户侧隐藏会话。"""
        self.user_deleted_at = datetime.utcnow()

    def hide_for_admin(self):
        """仅在管理员侧隐藏会话。"""
        self.admin_deleted_at = datetime.utcnow()

    def restore_for_user(self):
        """恢复用户侧可见性。"""
        self.user_deleted_at = None

    def restore_for_admin(self):
        """恢复管理员侧可见性。"""
        self.admin_deleted_at = None

    def can_purge(self):
        """双方都删除后，允许真正清理会话。"""
        return self.user_deleted_at is not None and self.admin_deleted_at is not None

    def purge_related_records(self):
        """彻底清理会话及其关联通知。"""
        from .notification import Notification

        Notification.query.filter_by(
            related_type='message',
            related_id=self.id
        ).delete(synchronize_session=False)
        db.session.delete(self)
    
    @classmethod
    def create_message_notification(cls, message):
        """创建新消息通知"""
        from .notification import Notification
        
        # 获取管理员用户（这里假设ID为1的用户是管理员）
        admin_user = db.session.query(db.Model.metadata.tables['user']).filter_by(id=1).first()
        if not admin_user:
            return None
            
        notification = Notification(
            user_id=1,  # 管理员用户ID
            type='message',
            title=f'新消息：{message.subject}',
            content=f'来自 {message.name} 的消息：{message.message[:100]}{"..." if len(message.message) > 100 else ""}',
            related_id=message.id,
            related_type='message',
            related_url=f'/admin/messages/{message.id}',
            sender_name=message.name
        )
        return notification


def ensure_message_schema():
    """兼容现有数据库，为消息表补齐单方删除所需字段。"""
    inspector = db.inspect(db.engine)
    if 'message' not in inspector.get_table_names():
        return

    existing_columns = {column['name'] for column in inspector.get_columns('message')}
    alter_statements = []

    if 'user_deleted_at' not in existing_columns:
        alter_statements.append('ALTER TABLE message ADD COLUMN user_deleted_at DATETIME')

    if 'admin_deleted_at' not in existing_columns:
        alter_statements.append('ALTER TABLE message ADD COLUMN admin_deleted_at DATETIME')

    if 'user_read_at' not in existing_columns:
        alter_statements.append('ALTER TABLE message ADD COLUMN user_read_at DATETIME')

    if not alter_statements:
        return

    with db.engine.begin() as conn:
        for statement in alter_statements:
            conn.execute(db.text(statement))
