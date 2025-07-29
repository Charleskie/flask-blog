from .filters import nl2br_filter
from functools import wraps
from flask import abort
from flask_login import current_user

__all__ = ['nl2br_filter', 'admin_required']

def admin_required(f):
    """管理员权限检查装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function 