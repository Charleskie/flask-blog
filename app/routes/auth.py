from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.models.user import db
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

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
            
            # 注册成功后自动登录用户
            login_user(user)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '注册成功！已自动登录。', 'redirect': url_for('main.index')})

            return redirect(url_for('main.index'))
            
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
        email = request.form.get('email', '').strip()
        
        if not email:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请输入邮箱地址'})
            return render_template('auth/forgot_password.html', error='请输入邮箱地址')
        
        # 验证邮箱格式
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请输入有效的邮箱地址'})
            return render_template('auth/forgot_password.html', error='请输入有效的邮箱地址')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                # 生成重置令牌
                token = user.generate_reset_token()
                
                # 发送重置邮件
                send_reset_email(user, token)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': '重置密码链接已发送到您的邮箱，请查收邮件并按照提示操作。'})
                
                return render_template('auth/forgot_password.html', 
                                     success='重置密码链接已发送到您的邮箱，请查收邮件并按照提示操作。')
                
            except Exception as e:
                print(f"发送重置邮件失败: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '发送邮件失败，请稍后重试'})
                return render_template('auth/forgot_password.html', error='发送邮件失败，请稍后重试')
        else:
            # 为了安全，不透露邮箱是否注册
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '如果该邮箱已注册，重置密码链接已发送到您的邮箱。'})
            return render_template('auth/forgot_password.html', 
                                 success='如果该邮箱已注册，重置密码链接已发送到您的邮箱。')

    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码页面"""
    # 验证token
    user = User.verify_reset_token_static(token)
    
    if not user:
        return render_template('auth/reset_password.html', 
                             error='重置链接无效或已过期，请重新申请。', 
                             token_valid=False)
    
    if request.method == 'POST':
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 验证密码
        if not password:
            return render_template('auth/reset_password.html', 
                                 error='请输入新密码', 
                                 token_valid=True, 
                                 token=token)
        
        if len(password) < 6:
            return render_template('auth/reset_password.html', 
                                 error='密码长度至少6位', 
                                 token_valid=True, 
                                 token=token)
        
        if password != confirm_password:
            return render_template('auth/reset_password.html', 
                                 error='两次输入的密码不一致', 
                                 token_valid=True, 
                                 token=token)
        
        try:
            # 更新密码
            user.password_hash = generate_password_hash(password)
            user.clear_reset_token()  # 清除重置令牌
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '密码重置成功，请使用新密码登录。', 'redirect': url_for('auth.login')})
            
            return render_template('auth/reset_password.html', 
                                 success='密码重置成功，请使用新密码登录。', 
                                 token_valid=False)
            
        except Exception as e:
            print(f"重置密码失败: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '重置密码失败，请稍后重试'})
            return render_template('auth/reset_password.html', 
                                 error='重置密码失败，请稍后重试', 
                                 token_valid=True, 
                                 token=token)
    
    return render_template('auth/reset_password.html', token_valid=True, token=token)

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

def send_reset_email(user, token):
    """发送重置密码邮件"""
    try:
        # 构建重置链接
        try:
            reset_url = url_for('auth.reset_password', token=token, _external=True)
        except RuntimeError:
            # 如果不在请求上下文中，手动构建URL
            base_url = current_app.config.get('SERVER_NAME', 'localhost:5000')
            scheme = current_app.config.get('PREFERRED_URL_SCHEME', 'http')
            reset_url = f"{scheme}://{base_url}/reset-password/{token}"
        
        # 邮件内容
        subject = "重置密码 - 我的个人网站"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>重置密码</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>重置密码</h1>
                </div>
                <div class="content">
                    <h2>您好，{user.get_display_name()}！</h2>
                    <p>您请求重置密码，请点击下面的按钮来设置新密码：</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">重置密码</a>
                    </p>
                    <p>如果按钮无法点击，请复制以下链接到浏览器地址栏：</p>
                    <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">
                        {reset_url}
                    </p>
                    <div class="warning">
                        <strong>安全提示：</strong>
                        <ul>
                            <li>此链接有效期为24小时</li>
                            <li>如果您没有请求重置密码，请忽略此邮件</li>
                            <li>为了账户安全，请不要将链接分享给他人</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复。</p>
                    <p>© 2024 我的个人网站</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        您好，{user.get_display_name()}！
        
        您请求重置密码，请访问以下链接来设置新密码：
        {reset_url}
        
        此链接有效期为24小时。
        如果您没有请求重置密码，请忽略此邮件。
        
        此邮件由系统自动发送，请勿回复。
        © 2024 我的个人网站
        """
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config.get('MAIL_FROM', 'noreply@example.com')
        msg['To'] = user.email
        
        # 添加文本和HTML内容
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # 发送邮件
        try:
            # 检查邮件配置
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            
            if not mail_server or not mail_username or not mail_password:
                # 如果没有配置邮件服务器，则只记录到日志
                current_app.logger.info(f"邮件配置不完整，模拟发送重置密码邮件给 {user.email}: {reset_url}")
                print(f"重置密码邮件发送给 {user.email}: {reset_url}")
                print("注意：邮件配置不完整，实际未发送邮件。请配置环境变量：")
                print("- MAIL_SERVER: SMTP服务器地址")
                print("- MAIL_USERNAME: 邮箱用户名")
                print("- MAIL_PASSWORD: 邮箱密码或应用专用密码")
                return True
            
            # 使用SMTP发送邮件
            server = smtplib.SMTP(mail_server, current_app.config.get('MAIL_PORT', 587))
            server.starttls()
            server.login(mail_username, mail_password)
            
            # 发送邮件
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"重置密码邮件成功发送给 {user.email}")
            print(f"重置密码邮件成功发送给 {user.email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"发送邮件失败: {e}")
            print(f"发送邮件失败: {e}")
            # 即使发送失败，也记录邮件内容到日志
            print(f"重置密码链接: {reset_url}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"构建邮件失败: {e}")
        print(f"构建邮件失败: {e}")
        return False 