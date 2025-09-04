from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Post, Project, Message, User
from app.models.user import db
from app.utils import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def admin():
    """管理后台首页"""
    # 统计数据
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status='published').count()
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status='active').count()
    total_messages = Message.query.count()
    unread_messages = Message.query.filter_by(status='unread').count()
    
    # 最近的文章
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    
    # 最近的项目
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    
    # 最近的消息
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('admin/admin.html',
                         total_posts=total_posts,
                         published_posts=published_posts,
                         total_projects=total_projects,
                         active_projects=active_projects,
                         total_messages=total_messages,
                         unread_messages=unread_messages,
                         recent_posts=recent_posts,
                         recent_projects=recent_projects,
                         recent_messages=recent_messages)

# 文章管理
@admin_bp.route('/admin/posts')
@login_required
@admin_required
def admin_posts():
    """文章管理页面"""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/admin_posts.html', posts=posts)

@admin_bp.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_post():
    """新建文章"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')
        tags = request.form.get('tags')
        featured_image = request.form.get('featured_image')
        status = request.form.get('status', 'draft')
        slug = request.form.get('slug')
        
        if not title or not content:
            flash('请填写标题和内容', 'error')
            return render_template('admin/new_post.html')
        
        try:
            post = Post(
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=tags,
                featured_image=featured_image,
                status=status,
                author_id=current_user.id
            )
            
            db.session.add(post)
            db.session.flush()  # 获取ID但不提交
            
            # 生成或使用提供的slug
            if slug:
                post.slug = slug
            else:
                post.slug = post.generate_slug()
            
            db.session.commit()
            
            flash('文章创建成功！', 'success')
            return redirect(url_for('admin.admin_posts'))
            
        except Exception as e:
            db.session.rollback()
            flash('创建失败，请稍后重试', 'error')
            print(f"创建文章错误: {e}")
    
    return render_template('admin/new_post.html')

@admin_bp.route('/admin/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(post_id):
    """编辑文章"""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category')
        tags = request.form.get('tags')
        featured_image = request.form.get('featured_image')
        status = request.form.get('status')
        slug = request.form.get('slug')
        
        if not title or not content:
            flash('请填写标题和内容', 'error')
            return render_template('admin/edit_post.html', post=post)
        
        try:
            post.title = title
            post.content = content
            post.excerpt = excerpt
            post.category = category
            post.tags = tags
            post.featured_image = featured_image
            post.status = status
            post.updated_at = datetime.utcnow()
            
            # 更新slug
            if slug:
                post.slug = slug
            else:
                post.slug = post.generate_slug()
            
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('admin.admin_posts'))
            
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请稍后重试', 'error')
            print(f"更新文章错误: {e}")
    
    return render_template('admin/edit_post.html', post=post)

@admin_bp.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(post_id):
    """删除文章"""
    post = Post.query.get_or_404(post_id)
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请稍后重试', 'error')
        print(f"删除文章错误: {e}")
    
    return redirect(url_for('admin.admin_posts'))

# 项目管理
@admin_bp.route('/admin/projects')
@login_required
@admin_required
def admin_projects():
    """项目管理页面"""
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/admin_projects.html', projects=projects)

@admin_bp.route('/admin/projects/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_project():
    """新建项目"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        short_description = request.form.get('short_description')
        image_url = request.form.get('image_url')
        github_url = request.form.get('github_url')
        live_url = request.form.get('live_url')
        demo_url = request.form.get('demo_url')
        status = request.form.get('status', 'active')
        category = request.form.get('category')
        tags = request.form.get('tags')
        technologies = request.form.get('technologies')
        features = request.form.get('features')
        challenges = request.form.get('challenges')
        lessons_learned = request.form.get('lessons_learned')
        featured = 'featured' in request.form
        
        if not title or not description:
            flash('请填写项目标题和描述', 'error')
            return render_template('admin/new_project.html')
        
        try:
            project = Project(
                title=title,
                description=description,
                short_description=short_description,
                image_url=image_url,
                github_url=github_url,
                live_url=live_url,
                demo_url=demo_url,
                status=status,
                category=category,
                tags=tags,
                technologies=technologies,
                features=features,
                challenges=challenges,
                lessons_learned=lessons_learned,
                featured=featured
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('项目创建成功！', 'success')
            return redirect(url_for('admin.admin_projects'))
            
        except Exception as e:
            db.session.rollback()
            flash('创建失败，请稍后重试', 'error')
            print(f"创建项目错误: {e}")
    
    return render_template('admin/new_project.html')

@admin_bp.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """编辑项目"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        short_description = request.form.get('short_description')
        image_url = request.form.get('image_url')
        github_url = request.form.get('github_url')
        live_url = request.form.get('live_url')
        demo_url = request.form.get('demo_url')
        status = request.form.get('status')
        category = request.form.get('category')
        tags = request.form.get('tags')
        technologies = request.form.get('technologies')
        features = request.form.get('features')
        challenges = request.form.get('challenges')
        lessons_learned = request.form.get('lessons_learned')
        featured = 'featured' in request.form
        
        if not title or not description:
            flash('请填写项目标题和描述', 'error')
            return render_template('admin/edit_project.html', project=project)
        
        try:
            project.title = title
            project.description = description
            project.short_description = short_description
            project.image_url = image_url
            project.github_url = github_url
            project.live_url = live_url
            project.demo_url = demo_url
            project.status = status
            project.category = category
            project.tags = tags
            project.technologies = technologies
            project.features = features
            project.challenges = challenges
            project.lessons_learned = lessons_learned
            project.featured = featured
            project.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('项目更新成功！', 'success')
            return redirect(url_for('admin.admin_projects'))
            
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请稍后重试', 'error')
            print(f"更新项目错误: {e}")
    
    return render_template('admin/edit_project.html', project=project)

@admin_bp.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """删除项目"""
    project = Project.query.get_or_404(project_id)
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('项目删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请稍后重试', 'error')
        print(f"删除项目错误: {e}")
    
    return redirect(url_for('admin.admin_projects'))

# 消息管理
@admin_bp.route('/admin/messages')
@login_required
def admin_messages():
    """消息管理页面"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Message.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    messages = query.order_by(Message.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/admin_messages.html', messages=messages, status_filter=status_filter)

@admin_bp.route('/admin/messages/<int:message_id>')
@login_required
def view_message(message_id):
    """查看消息详情"""
    message = Message.query.get_or_404(message_id)
    
    # 标记为已读
    if message.is_unread():
        message.mark_as_read()
        db.session.commit()
    
    return render_template('admin/view_message.html', message=message)

@admin_bp.route('/admin/messages/<int:message_id>/reply', methods=['GET', 'POST'])
@login_required
def reply_message(message_id):
    """回复消息"""
    message = Message.query.get_or_404(message_id)
    
    if request.method == 'POST':
        reply_content = request.form.get('reply_content')
        
        if not reply_content:
            flash('请填写回复内容', 'error')
            return render_template('admin/reply_message.html', message=message)
        
        try:
            # 这里可以添加发送邮件的逻辑
            message.mark_as_replied()
            db.session.commit()
            
            flash('回复已发送！', 'success')
            return redirect(url_for('admin.admin_messages'))
            
        except Exception as e:
            db.session.rollback()
            flash('发送失败，请稍后重试', 'error')
            print(f"回复消息错误: {e}")
    
    return render_template('admin/reply_message.html', message=message)

@admin_bp.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """删除消息"""
    message = Message.query.get_or_404(message_id)
    
    try:
        db.session.delete(message)
        db.session.commit()
        flash('消息删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请稍后重试', 'error')
        print(f"删除消息错误: {e}")
    
    return redirect(url_for('admin.admin_messages'))

@admin_bp.route('/admin/messages/<int:message_id>/status', methods=['POST'])
@login_required
def change_message_status(message_id):
    """更改消息状态"""
    message = Message.query.get_or_404(message_id)
    new_status = request.form.get('status')
    
    if new_status in ['unread', 'read', 'replied', 'archived']:
        try:
            message.status = new_status
            if new_status == 'read' and not message.read_at:
                message.read_at = datetime.utcnow()
            elif new_status == 'replied' and not message.replied_at:
                message.replied_at = datetime.utcnow()
            
            db.session.commit()
            flash('状态更新成功！', 'success')
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请稍后重试', 'error')
            print(f"更新消息状态错误: {e}")
    
    return redirect(url_for('admin.admin_messages')) 