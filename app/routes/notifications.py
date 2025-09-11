from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import db
from app.models import Notification
from app.utils import admin_required

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications')
@login_required
def notifications():
    """消息通知列表页面"""
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', '')
    
    query = Notification.query.filter_by(user_id=current_user.id)
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('notifications/notifications.html', 
                         notifications=notifications, 
                         type_filter=type_filter)

@notification_bp.route('/api/notifications/unread-count')
@login_required
def unread_count():
    """获取未读消息数量"""
    count = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).count()
    
    return jsonify({'count': count})

@notification_bp.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """标记所有消息为已读"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).update({'is_read': True, 'read_at': db.func.now()})
        
        db.session.commit()
        return jsonify({'success': True, 'message': '所有消息已标记为已读'})
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
    
    # 如果有跳转URL，则跳转
    if notification.related_url:
        return redirect(notification.related_url)
    
    return redirect(url_for('notification.notifications'))
