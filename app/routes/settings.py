from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import db, User
from datetime import datetime
import os
import secrets

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings():
    """设置页面主入口"""
    return render_template('settings/index.html')

@settings_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    """个人信息设置"""
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        bio = request.form.get('bio', '').strip()
        website = request.form.get('website', '').strip()
        location = request.form.get('location', '').strip()
        company = request.form.get('company', '').strip()
        job_title = request.form.get('job_title', '').strip()
        phone = request.form.get('phone', '').strip()
        
        try:
            current_user.nickname = nickname
            current_user.bio = bio
            current_user.website = website
            current_user.location = location
            current_user.company = company
            current_user.job_title = job_title
            current_user.phone = phone
            
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '个人信息更新成功！'})

            return redirect(url_for('settings.profile_settings'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

            print(f"更新个人信息错误: {e}")
    
    return render_template('settings/profile.html')

@settings_bp.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account_settings():
    """账户设置"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 验证当前密码（只有在修改密码时才需要）
        if new_password and not check_password_hash(current_user.password_hash, current_password):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '当前密码错误'})

            return render_template('settings/account.html')
        
        # 检查用户名是否已被其他用户使用
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '用户名已被使用'})

            return render_template('settings/account.html')
        
        # 检查邮箱是否已被其他用户使用
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != current_user.id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '邮箱已被使用'})

            return render_template('settings/account.html')
        
        try:
            # 更新用户信息（用户名不允许更改，保持原值）
            if username and username.strip():
                current_user.username = username.strip()
            if email and email.strip():
                current_user.email = email.strip()
            
            # 如果提供了新密码，则更新密码
            if new_password:
                if new_password != confirm_password:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': '两次输入的新密码不一致'})

                    return render_template('settings/account.html')
                current_user.password_hash = generate_password_hash(new_password)
            
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '账户信息更新成功！'})

            return redirect(url_for('settings.account_settings'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

            print(f"更新账户信息错误: {e}")
    
    return render_template('settings/account.html')


@settings_bp.route('/settings/security', methods=['GET', 'POST'])
@login_required
def security_settings():
    """安全设置"""
    if request.method == 'POST':
        login_notifications = request.form.get('login_notifications') == 'on'
        session_timeout = int(request.form.get('session_timeout', 30))
        
        try:
            current_user.login_notifications = login_notifications
            current_user.session_timeout = session_timeout
            
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '安全设置更新成功！'})

            return redirect(url_for('settings.security_settings'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

            print(f"更新安全设置错误: {e}")
    
    return render_template('settings/security.html')

@settings_bp.route('/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    """隐私设置"""
    if request.method == 'POST':
        profile_public = request.form.get('profile_public') == 'on'
        show_email = request.form.get('show_email') == 'on'
        show_phone = request.form.get('show_phone') == 'on'
        
        try:
            current_user.profile_public = profile_public
            current_user.show_email = show_email
            current_user.show_phone = show_phone
            
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '隐私设置更新成功！'})

            return redirect(url_for('settings.privacy_settings'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

            print(f"更新隐私设置错误: {e}")
    
    return render_template('settings/privacy.html')

@settings_bp.route('/settings/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """上传头像"""
    if 'avatar' not in request.files:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '没有选择文件'})

        return redirect(url_for('settings.profile_settings'))
    
    file = request.files['avatar']
    if file.filename == '':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '没有选择文件'})

        return redirect(url_for('settings.profile_settings'))
    
    if file:
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if '.' not in file.filename or \
           file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '不支持的文件类型，支持：PNG、JPG、JPEG、GIF、WebP'})

            return redirect(url_for('settings.profile_settings'))
        
        # 检查文件大小 (最大5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '文件大小不能超过5MB'})

            return redirect(url_for('settings.profile_settings'))
        
        try:
            # 生成唯一文件名
            filename = f"avatar_{current_user.id}_{secrets.token_hex(8)}.{file.filename.rsplit('.', 1)[1].lower()}"
            
            # 确保上传目录存在
            upload_dir = os.path.join('app', 'static', 'uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)
            
            # 删除旧头像（如果不是默认头像）
            if current_user.avatar and '/static/uploads/avatars/' in current_user.avatar:
                try:
                    old_avatar_path = os.path.join('app', current_user.avatar.lstrip('/'))
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                except Exception as e:
                    print(f"删除旧头像失败: {e}")
            
            # 更新用户头像URL
            current_user.avatar = f'/static/uploads/avatars/{filename}'
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': '头像上传成功！',
                    'avatar_url': current_user.avatar
                })
            
            flash('头像上传成功！', 'success')
            return redirect(url_for('settings.profile_settings'))

        except Exception as e:
            db.session.rollback()
            print(f"头像上传错误: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '头像上传失败，请稍后重试'})
            
            flash('头像上传失败，请稍后重试', 'error')
    
    return redirect(url_for('settings.profile_settings'))
