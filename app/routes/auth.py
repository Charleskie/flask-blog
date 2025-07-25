from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.models.user import db

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
            flash('登录成功！', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证输入
        if not username or not email or not password:
            flash('请填写所有必填字段', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('auth/register.html')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('auth/register.html')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('auth/register.html')
        
        try:
            # 创建新用户
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试', 'error')
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
            flash('重置密码链接已发送到您的邮箱', 'success')
        else:
            flash('该邮箱未注册', 'error')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码页面"""
    # 这里可以添加验证token的逻辑
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('auth/reset_password.html')
        
        # 这里可以添加更新密码的逻辑
        flash('密码重置成功！请登录。', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已成功登出', 'success')
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
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证当前密码
        if not check_password_hash(current_user.password_hash, current_password):
            flash('当前密码错误', 'error')
            return render_template('auth/edit_profile.html')
        
        # 检查用户名是否已被其他用户使用
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('用户名已被使用', 'error')
            return render_template('auth/edit_profile.html')
        
        # 检查邮箱是否已被其他用户使用
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != current_user.id:
            flash('邮箱已被使用', 'error')
            return render_template('auth/edit_profile.html')
        
        try:
            # 更新用户信息
            current_user.username = username
            current_user.email = email
            
            # 如果提供了新密码，则更新密码
            if new_password:
                    if new_password != confirm_password:
                        flash('两次输入的新密码不一致', 'error')
                        return render_template('auth/edit_profile.html')
            current_user.password_hash = generate_password_hash(new_password)
            
            db.session.commit()
            flash('资料更新成功！', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请稍后重试', 'error')
            print(f"更新用户资料错误: {e}")
    
    return render_template('auth/edit_profile.html') 