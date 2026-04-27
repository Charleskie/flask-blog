from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.models.user import db
from app.models import Notification

notification_bp = Blueprint('notification', __name__)

CONVERSATION_NOTIFICATION_TYPES = ('message', 'message_reply')
NOTIFICATION_FILTER_GROUPS = (
    {'key': 'all', 'param': '', 'label': '全部提醒', 'types': None},
    {'key': 'read', 'param': 'read', 'label': '已读', 'types': None, 'is_read': True},
    {'key': 'comment', 'param': 'comment', 'label': '评论', 'types': ('comment',)},
    {'key': 'reply', 'param': 'reply', 'label': '回复', 'types': ('reply',)},
    {'key': 'interaction', 'param': 'interaction', 'label': '互动', 'types': ('like', 'favorite', 'rating')},
)
NOTIFICATION_FILTER_ALIASES = {
    '': 'all',
    'comment': 'comment',
    'read': 'read',
    'is_read': 'read',
    'readed': 'read',
    'reply': 'reply',
    'interaction': 'interaction',
    'like': 'interaction',
    'favorite': 'interaction',
    'rating': 'interaction',
    'like,favorite': 'interaction',
}


def _visible_notifications_query(user_id):
    """返回通知中心可见的提醒，排除私信/对话类通知。"""
    return Notification.query.filter(
        Notification.user_id == user_id,
        Notification.type.notin_(CONVERSATION_NOTIFICATION_TYPES),
        or_(Notification.related_type.is_(None), Notification.related_type != 'project'),
        or_(Notification.related_url.is_(None), ~Notification.related_url.like('/projects%')),
    )


def _resolve_filter_group(filter_value):
    """将旧筛选参数归一到新的分组定义。"""
    filter_key = NOTIFICATION_FILTER_ALIASES.get((filter_value or '').strip(), 'all')
    return next(group for group in NOTIFICATION_FILTER_GROUPS if group['key'] == filter_key)

@notification_bp.route('/notifications')
@login_required
def notifications():
    """消息通知列表页面"""
    page = request.args.get('page', 1, type=int)
    active_filter = _resolve_filter_group(request.args.get('type', ''))

    base_query = _visible_notifications_query(current_user.id)
    query = base_query

    if active_filter.get('types'):
        query = query.filter(Notification.type.in_(active_filter['types']))
    if 'is_read' in active_filter:
        query = query.filter_by(is_read=active_filter['is_read'])

    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    unread_total = base_query.filter_by(is_read=False).count()
    filter_options = []
    for group in NOTIFICATION_FILTER_GROUPS:
        group_query = base_query
        if group.get('types'):
            group_query = group_query.filter(Notification.type.in_(group['types']))
        if 'is_read' in group:
            group_query = group_query.filter_by(is_read=group['is_read'])

        filter_options.append({
            **group,
            'href': url_for('notification.notifications', type=group['param']) if group['param'] else url_for('notification.notifications'),
            'count': group_query.count(),
            'active': group['key'] == active_filter['key'],
        })

    return render_template(
        'notifications/notifications.html',
        notifications=notifications,
        type_filter=active_filter['param'],
        active_filter=active_filter,
        filter_options=filter_options,
        unread_total=unread_total,
        visible_total=filter_options[0]['count'],
    )

@notification_bp.route('/api/notifications/unread-count')
@login_required
def unread_count():
    """获取未读消息数量"""
    count = _visible_notifications_query(current_user.id).filter_by(
        is_read=False
    ).count()
    
    return jsonify({'count': count})

@notification_bp.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """标记所有消息为已读"""
    try:
        updated_count = _visible_notifications_query(current_user.id).filter_by(
            is_read=False
        ).update({'is_read': True, 'read_at': db.func.now()}, synchronize_session=False)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '所有消息已标记为已读', 'count': updated_count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败'})

@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """标记单个消息为已读"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        return jsonify({'success': False, 'message': '消息不存在'})
    
    try:
        notification.mark_as_read()
        db.session.commit()
        return jsonify({'success': True, 'message': '消息已标记为已读'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败'})

@notification_bp.route('/api/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """删除消息"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        return jsonify({'success': False, 'message': '消息不存在'})
    
    try:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'success': True, 'message': '消息已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '删除失败'})

@notification_bp.route('/notifications/<int:notification_id>')
@login_required
def view_notification(notification_id):
    """查看消息详情并跳转"""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first()
    
    if not notification:
        return redirect(url_for('notification.notifications'))
    
    # 标记为已读
    if not notification.is_read:
        notification.mark_as_read()
        db.session.commit()
    
    if notification.related_type == 'project' or (notification.related_url or '').startswith('/projects'):
        flash('这条通知关联的内容已移除', 'info')
        return redirect(url_for('notification.notifications'))

    # 如果有跳转URL，则跳转
    if notification.related_url:
        return redirect(notification.related_url)
    
    return redirect(url_for('notification.notifications'))
