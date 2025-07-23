from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///personal_website.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

@app.route('/projects')
def projects():
    """项目展示页面"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)

@app.route('/blog')
def blog():
    """博客页面"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False)
    return render_template('blog.html', posts=posts)

@app.route('/contact')
def contact():
    """联系页面"""
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
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
            return render_template('register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return render_template('register.html')
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        # 创建新用户
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试', 'error')
            print(f"注册错误: {e}")
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码页面"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('请输入邮箱地址', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        if user:
            # 这里可以添加发送重置密码邮件的逻辑
            # 为了演示，我们只是显示一个消息
            flash('如果该邮箱已注册，重置密码链接将发送到您的邮箱', 'success')
        else:
            # 为了安全，即使邮箱不存在也显示相同消息
            flash('如果该邮箱已注册，重置密码链接将发送到您的邮箱', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码页面"""
    # 这里应该验证token的有效性
    # 为了演示，我们假设token是有效的
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('请填写所有字段', 'error')
            return render_template('reset_password.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('reset_password.html')
        
        if len(password) < 6:
            flash('密码长度至少6位', 'error')
            return render_template('reset_password.html')
        
        # 这里应该根据token找到用户并更新密码
        # 为了演示，我们只是显示成功消息
        flash('密码重置成功！请使用新密码登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    """管理后台"""
    return render_template('admin.html')

@app.route('/profile')
@login_required
def profile():
    """用户个人资料页面"""
    return render_template('profile.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 更新邮箱
        if email and email != current_user.email:
            # 检查邮箱是否已被其他用户使用
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != current_user.id:
                flash('该邮箱已被其他用户使用', 'error')
                return render_template('edit_profile.html')
            
            current_user.email = email
            flash('邮箱更新成功', 'success')
        
        # 更新密码
        if current_password and new_password:
            if not check_password_hash(current_user.password_hash, current_password):
                flash('当前密码错误', 'error')
                return render_template('edit_profile.html')
            
            if new_password != confirm_password:
                flash('两次输入的新密码不一致', 'error')
                return render_template('edit_profile.html')
            
            if len(new_password) < 6:
                flash('新密码长度至少6位', 'error')
                return render_template('edit_profile.html')
            
            current_user.password_hash = generate_password_hash(new_password)
            flash('密码更新成功', 'success')
        
        try:
            db.session.commit()
            flash('个人资料更新成功', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请稍后重试', 'error')
            print(f"更新个人资料错误: {e}")
    
    return render_template('edit_profile.html')

# 错误处理
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 