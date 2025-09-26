from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.models.user import db
import os
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # 检查是否是AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '登录成功！', 'redirect': url_for('main.index')})

            return redirect(url_for('main.index'))
        else:
            # 检查是否是AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '用户名或密码错误'})

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证输入
        if not username or not email or not password:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template('auth/register.html')
        
        if password != confirm_password:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '两次输入的密码不一致'})

            return render_template('auth/register.html')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '用户名已存在'})

            return render_template('auth/register.html')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '邮箱已被注册'})

            return render_template('auth/register.html')
        
        # 处理头像上传
        avatar_file = None
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and avatar_file.filename != '':
                # 检查文件类型
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                if '.' not in avatar_file.filename or \
                   avatar_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': '不支持的文件类型，支持：PNG、JPG、JPEG、GIF、WebP'})
                    return render_template('auth/register.html')
                
                # 检查文件大小 (最大5MB)
                avatar_file.seek(0, os.SEEK_END)
                file_size = avatar_file.tell()
                avatar_file.seek(0)  # 重置文件指针
                
                if file_size > 5 * 1024 * 1024:  # 5MB
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': '文件大小不能超过5MB'})
                    return render_template('auth/register.html')
        
        try:
            # 创建新用户
            user = User(
                username=username,
                nickname=nickname or username,  # 如果没有提供昵称，使用用户名
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.flush()  # 获取用户ID，但不提交事务
            
            # 如果有头像文件，保存头像
            if avatar_file and avatar_file.filename != '':
                # 生成唯一文件名
                filename = f"avatar_{user.id}_{secrets.token_hex(8)}.{avatar_file.filename.rsplit('.', 1)[1].lower()}"
                
                # 确保上传目录存在
                upload_dir = os.path.join('app', 'static', 'uploads', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                
                # 保存文件
                file_path = os.path.join(upload_dir, filename)
                avatar_file.save(file_path)
                
                # 更新用户头像URL
                user.avatar = f'/static/uploads/avatars/{filename}'
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '注册成功！请登录。', 'redirect': url_for('auth.login')})

            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '注册失败，请稍后重试'})

            print(f"注册错误: {e}")
    
    return render_template('auth/register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码页面"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # 这里可以添加发送重置密码邮件的逻辑
            return jsonify({'success': False, 'message': '重置密码链接已发送到您的邮箱'})
        else:
            return jsonify({'error': False, 'message': '该邮箱未注册'})

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码页面"""
    # 这里可以添加验证token的逻辑
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:

            return render_template('auth/reset_password.html')
        
        # 这里可以添加更新密码的逻辑

        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': '已成功登出', 'redirect': url_for('main.index')})

    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """用户资料页面"""
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑用户资料"""
    if request.method == 'POST':
        # 获取表单数据
        nickname = request.form.get('nickname', '').strip()
        bio = request.form.get('bio', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 验证当前密码（只有在修改密码时才需要）
        if new_password and not check_password_hash(current_user.password_hash, current_password):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '当前密码错误'})
            return render_template('auth/edit_profile.html')
        
        # 检查邮箱是否已被其他用户使用
        if email and email != current_user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != current_user.id:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '邮箱已被使用'})
                return render_template('auth/edit_profile.html')
        
        try:
            # 更新用户信息
            if nickname:
                current_user.nickname = nickname
            if bio:
                current_user.bio = bio
            if email:
                current_user.email = email
            
            # 如果提供了新密码，则更新密码
            if new_password:
                if new_password != confirm_password:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'success': False, 'message': '两次输入的新密码不一致'})
                    return render_template('auth/edit_profile.html')
                current_user.password_hash = generate_password_hash(new_password)
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '个人资料更新成功！'})
            
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})
            
            print(f"更新用户资料错误: {e}")
    
    return render_template('auth/edit_profile.html') 