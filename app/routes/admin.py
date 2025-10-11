from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app.models import Post, Project, Message, User, AboutContent, AboutContact, Skill
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
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    # 构建查询
    query = Post.query
    
    # 状态筛选
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # 搜索功能
    if search_query:
        query = query.filter(
            db.or_(
                Post.title.contains(search_query),
                Post.content.contains(search_query),
                Post.excerpt.contains(search_query),
                Post.category.contains(search_query),
                Post.tags.contains(search_query)
            )
        )
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/admin_posts.html', 
                         posts=posts, 
                         status_filter=status_filter,
                         search_query=search_query)

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '请填写标题和内容'})

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
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '文章创建成功！'})

            return redirect(url_for('admin.admin_posts'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '创建失败，请稍后重试'})

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '请填写标题和内容'})

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '文章更新成功！'})

            return redirect(url_for('admin.admin_posts'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '文章删除成功！'})

    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})

        print(f"删除文章错误: {e}")
    
    return redirect(url_for('admin.admin_posts'))

# 项目管理
@admin_bp.route('/admin/projects')
@login_required
@admin_required
def admin_projects():
    """项目管理页面"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    # 构建查询
    query = Project.query
    
    # 状态筛选
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # 搜索功能
    if search_query:
        query = query.filter(
            db.or_(
                Project.title.contains(search_query),
                Project.description.contains(search_query),
                Project.short_description.contains(search_query),
                Project.category.contains(search_query),
                Project.tags.contains(search_query),
                Project.technologies.contains(search_query)
            )
        )
    
    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/admin_projects.html', 
                         projects=projects, 
                         status_filter=status_filter,
                         search_query=search_query)

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写项目标题和描述'})

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
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '项目创建成功！'})

            return redirect(url_for('admin.admin_projects'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '创建失败，请稍后重试'})

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写项目标题和描述'})

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
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '项目更新成功！'})

            return redirect(url_for('admin.admin_projects'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '项目删除成功！'})

    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})

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
    from app.models import MessageReply
    from app.utils.email_sender import send_reply_email
    
    message = Message.query.get_or_404(message_id)
    
    if request.method == 'POST':
        reply_content = request.form.get('reply_content')
        
        if not reply_content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写回复内容'})

            return render_template('admin/reply_message.html', message=message)
        
        try:
            # 创建回复记录
            reply_record = MessageReply.create_reply(
                message_id=message.id,
                reply_content=reply_content,
                reply_type='admin',
                sender_name=current_user.username if current_user else '管理员',
                sender_email=current_user.email if current_user else 'admin@shiheng.info'
            )
            
            db.session.add(reply_record)
            db.session.flush()  # 获取回复ID
            
            # 标记原消息为已回复
            message.mark_as_replied()
            
            # 发送邮件给用户
            email_sent = send_reply_email(message, reply_content, reply_record)
            
            # 更新回复记录的发送状态
            if email_sent:
                reply_record.mark_as_sent()
            
            # 创建私信回复通知（如果消息发送者是注册用户）
            from app.models import User
            message_user = User.query.filter_by(email=message.email).first()
            if message_user:
                from app.models import Notification
                notification = Notification.create_message_reply_notification(
                    message_author_id=message_user.id,
                    admin_name=current_user.username if current_user else '管理员',
                    message_subject=message.subject,
                    message_id=message.id
                )
                db.session.add(notification)
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                success_message = '回复已发送！'
                if email_sent:
                    success_message += ' 邮件已发送给用户。'
                else:
                    success_message += ' 但邮件发送失败，请检查邮件配置。'
                return jsonify({'success': True, 'message': success_message})

            return redirect(url_for('admin.view_message', message_id=message.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"回复消息错误: {e}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '发送失败，请稍后重试'})

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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '消息删除成功！'})
        flash('消息删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
        flash('删除失败，请稍后重试', 'error')
        print(f"删除消息错误: {e}")
    
    return redirect(url_for('admin.admin_messages'))

@admin_bp.route('/admin/messages/<int:message_id>/replies/<int:reply_id>/delete', methods=['POST'])
@login_required
def delete_message_reply(message_id, reply_id):
    """删除消息回复"""
    from app.models import MessageReply
    
    message = Message.query.get_or_404(message_id)
    reply = MessageReply.query.filter_by(id=reply_id, message_id=message_id).first_or_404()
    
    try:
        # 删除回复
        db.session.delete(reply)
        
        # 检查是否还有其他回复
        remaining_replies = MessageReply.query.filter_by(message_id=message_id).count()
        
        # 如果没有回复了，更新消息状态
        if remaining_replies == 0:
            if message.status == 'in_conversation':
                message.status = 'read'  # 回到已读状态
            elif message.status == 'replied':
                message.status = 'read'  # 回到已读状态
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': '回复删除成功！',
                'remaining_replies': remaining_replies
            })
        
        return redirect(url_for('admin.view_message', message_id=message_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除回复错误: {e}", exc_info=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
        
        print(f"删除回复错误: {e}")
        return redirect(url_for('admin.view_message', message_id=message_id))

@admin_bp.route('/admin/messages/<int:message_id>/replies/batch-delete', methods=['POST'])
@login_required
def batch_delete_message_replies(message_id):
    """批量删除消息回复"""
    from app.models import MessageReply
    
    message = Message.query.get_or_404(message_id)
    
    try:
        data = request.get_json()
        reply_ids = data.get('reply_ids', [])
        
        if not reply_ids:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请选择要删除的回复'})
            return redirect(url_for('admin.view_message', message_id=message_id))
        
        # 删除选中的回复
        deleted_count = 0
        for reply_id in reply_ids:
            reply = MessageReply.query.filter_by(id=reply_id, message_id=message_id).first()
            if reply:
                db.session.delete(reply)
                deleted_count += 1
        
        # 检查是否还有其他回复
        remaining_replies = MessageReply.query.filter_by(message_id=message_id).count()
        
        # 如果没有回复了，更新消息状态
        if remaining_replies == 0:
            if message.status == 'in_conversation':
                message.status = 'read'  # 回到已读状态
            elif message.status == 'replied':
                message.status = 'read'  # 回到已读状态
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': f'成功删除 {deleted_count} 条回复！',
                'deleted_count': deleted_count,
                'remaining_replies': remaining_replies
            })
        
        return redirect(url_for('admin.view_message', message_id=message_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"批量删除回复错误: {e}", exc_info=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '批量删除失败，请稍后重试'})
        
        print(f"批量删除回复错误: {e}")
        return redirect(url_for('admin.view_message', message_id=message_id))

@admin_bp.route('/admin/messages/<int:message_id>/status', methods=['POST'])
@login_required
def change_message_status(message_id):
    """更改消息状态"""
    message = Message.query.get_or_404(message_id)
    new_status = request.form.get('status')
    
    if new_status not in ['unread', 'read', 'replied', 'archived']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '无效的状态'})
        flash('无效的状态', 'error')
        return redirect(url_for('admin.admin_messages'))
    
    try:
        message.status = new_status
        if new_status == 'read' and not message.read_at:
            message.read_at = datetime.utcnow()
        elif new_status == 'replied' and not message.replied_at:
            message.replied_at = datetime.utcnow()
        
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '状态更新成功！'})
        flash('状态更新成功！', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '状态更新失败，请稍后重试'})
        flash('状态更新失败，请稍后重试', 'error')
        print(f"更新消息状态错误: {e}")
    
    return redirect(url_for('admin.admin_messages'))


# 关于页面管理
@admin_bp.route('/admin/about')
@login_required
@admin_required
def admin_about():
    """关于页面管理"""
    # 获取当前关于页面内容
    about_content = AboutContent.query.filter_by(section='main_content').first()
    
    return render_template('admin/admin_about.html', about_content=about_content)

@admin_bp.route('/admin/about/content/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_about_content():
    """新建关于页面内容"""
    if request.method == 'POST':
        section = request.form.get('section')
        title = request.form.get('title')
        content = request.form.get('content')
        order = request.form.get('orde', 0, type=int)
        is_active = 'is_active' in request.form
        
        if not section or not title or not content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template('admin/new_about_content.html')
        
        try:
            about_content = AboutContent(
                section=section,
                title=title,
                content=content,
                order=order,
                is_active=is_active
            )
            
            db.session.add(about_content)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '内容创建成功！'})

            return redirect(url_for('admin.admin_about'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '创建失败，请稍后重试'})

            print(f"创建关于页面内容错误: {e}")
    
    return render_template('admin/new_about_content.html')

@admin_bp.route('/admin/about/content/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_about_content(content_id):
    """编辑关于页面内容"""
    content = AboutContent.query.get_or_404(content_id)
    
    if request.method == 'POST':
        section = request.form.get('section')
        title = request.form.get('title')
        content_text = request.form.get('content')
        order = request.form.get('orde', 0, type=int)
        is_active = 'is_active' in request.form
        
        if not section or not title or not content_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template('admin/edit_about_content.html', content=content)
        
        try:
            content.section = section
            content.title = title
            content.content = content_text
            content.order = order
            content.is_active = is_active
            content.updated_at = datetime.utcnow()
            
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '内容更新成功！'})

            return redirect(url_for('admin.admin_about'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

            print(f"更新关于页面内容错误: {e}")
    
    return render_template('admin/edit_about_content.html', content=content)

@admin_bp.route('/admin/about/content/<int:content_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_about_content(content_id):
    """删除关于页面内容"""
    content = AboutContent.query.get_or_404(content_id)
    
    try:
        db.session.delete(content)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '内容删除成功！'})

    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})

        print(f"删除关于页面内容错误: {e}")
    
    return redirect(url_for('admin.admin_about'))

@admin_bp.route('/admin/about/contact/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_about_contact():
    """新建联系方式"""
    if request.method == 'POST':
        platform = request.form.get('platform')
        icon = request.form.get('icon')
        url = request.form.get('url')
        text = request.form.get('text')
        color = request.form.get('colo', 'primary')
        order = request.form.get('orde', 0, type=int)
        is_active = 'is_active' in request.form
        
        if not platform or not icon or not text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template('admin/new_about_contact.html')
        
        try:
            contact = AboutContact(
                platform=platform,
                icon=icon,
                url=url,
                text=text,
                color=color,
                order=order,
                is_active=is_active
            )
            
            db.session.add(contact)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '联系方式创建成功！'})

            return redirect(url_for('admin.admin_about'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '创建失败，请稍后重试'})

            print(f"创建联系方式错误: {e}")
    
    return render_template('admin/new_about_contact.html')

@admin_bp.route('/admin/about/contact/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_about_contact(contact_id):
    """编辑联系方式"""
    contact = AboutContact.query.get_or_404(contact_id)
    
    if request.method == 'POST':
        platform = request.form.get('platform')
        icon = request.form.get('icon')
        url = request.form.get('url')
        text = request.form.get('text')
        color = request.form.get('colo', 'primary')
        order = request.form.get('orde', 0, type=int)
        is_active = 'is_active' in request.form
        
        if not platform or not icon or not text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template('admin/edit_about_contact.html', contact=contact)
        
        try:
            contact.platform = platform
            contact.icon = icon
            contact.url = url
            contact.text = text
            contact.color = color
            contact.order = order
            contact.is_active = is_active
            contact.updated_at = datetime.utcnow()
            
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '联系方式更新成功！'})

            return redirect(url_for('admin.admin_about'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})

            print(f"更新联系方式错误: {e}")
    
    return render_template('admin/edit_about_contact.html', contact=contact)

@admin_bp.route('/admin/about/contact/<int:contact_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_about_contact(contact_id):
    """删除联系方式"""
    contact = AboutContact.query.get_or_404(contact_id)
    
    try:
        db.session.delete(contact)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '联系方式删除成功！'})

    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})

        print(f"删除联系方式错误: {e}")
    
    return redirect(url_for('admin.admin_about'))


# 技能管理
@admin_bp.route('/admin/skills')
@login_required
@admin_required
def admin_skills():
    """技能管理页面"""
    page = request.args.get('page', 1, type=int)
    skills = Skill.query.order_by(Skill.sort_order.asc(), Skill.name.asc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/admin_skills.html', skills=skills)


@admin_bp.route('/admin/skills/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_skill():
    """新建技能"""
    if request.method == 'POST':
        try:
            skill = Skill(
                name=request.form.get('name'),
                icon=request.form.get('icon'),
                proficiency=int(request.form.get('proficiency', 0)),
                category=request.form.get('category'),
                description=request.form.get('description'),
                sort_order=int(request.form.get('sort_order', 0)),
                is_active=request.form.get('is_active') == 'on'
            )
            
            db.session.add(skill)
            db.session.commit()
            flash('技能创建成功！', 'success')
            return redirect(url_for('admin.admin_skills'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败：{str(e)}', 'error')
            print(f"创建技能错误: {e}")
    
    return render_template('admin/new_skill.html')


@admin_bp.route('/admin/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_skill(skill_id):
    """编辑技能"""
    skill = Skill.query.get_or_404(skill_id)
    
    if request.method == 'POST':
        try:
            skill.name = request.form.get('name')
            skill.icon = request.form.get('icon')
            skill.proficiency = int(request.form.get('proficiency', 0))
            skill.category = request.form.get('category')
            skill.description = request.form.get('description')
            skill.sort_order = int(request.form.get('sort_order', 0))
            skill.is_active = request.form.get('is_active') == 'on'
            skill.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('技能更新成功！', 'success')
            return redirect(url_for('admin.admin_skills'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')
            print(f"更新技能错误: {e}")
    
    return render_template('admin/edit_skill.html', skill=skill)


@admin_bp.route('/admin/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_skill(skill_id):
    """删除技能"""
    skill = Skill.query.get_or_404(skill_id)
    
    try:
        db.session.delete(skill)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '技能删除成功！'})
        flash('技能删除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
        flash('删除失败，请稍后重试', 'error')
        print(f"删除技能错误: {e}")
    
    return redirect(url_for('admin.admin_skills'))


@admin_bp.route('/api/skills')
def api_skills():
    """API: 获取技能列表"""
    category = request.args.get('category')
    skills = Skill.get_active_skills(category=category)
    return jsonify([skill.to_dict() for skill in skills])


@admin_bp.route('/api/skills/categories')
def api_skill_categories():
    """API: 获取技能分类"""
    categories = db.session.query(Skill.category).filter(
        Skill.is_active == True,
        Skill.category.isnot(None)
    ).distinct().all()
    return jsonify([cat[0] for cat in categories if cat[0]])


@admin_bp.route('/admin/messages/mark-all-read', methods=['POST'])
@login_required
@admin_required
def mark_all_messages_read():
    """一键标记所有未读消息为已读"""
    try:
        # 获取所有未读消息
        unread_messages = Message.query.filter_by(status='unread').all()
        count = len(unread_messages)
        
        if count == 0:
            return jsonify({
                'success': True,
                'count': 0,
                'message': '没有未读消息'
            })
        
        # 批量更新状态
        for message in unread_messages:
            message.mark_as_read()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'count': count,
            'message': f'已成功标记 {count} 条消息为已读'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '操作失败，请稍后重试',
            'error': str(e)
        }), 500

@admin_bp.route('/api/messages/unread-count')
@login_required
@admin_required
def api_unread_messages_count():
    """API: 获取未读消息数量"""
    try:
        unread_count = Message.query.filter_by(status='unread').count()
        return jsonify({
            'success': True,
            'count': unread_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'count': 0,
            'error': str(e)
        }), 500


# 简化的关于页面编辑
@admin_bp.route('/admin/about/simple', methods=['GET', 'POST'])
@login_required
@admin_required
def simple_about_edit():
    """简化的关于页面编辑"""
    if request.method == 'POST':
        page_title = request.form.get('page_title')
        page_content = request.form.get('page_content')
        meta_description = request.form.get('meta_description', '')
        meta_keywords = request.form.get('meta_keywords', '')
        is_active = 'is_active' in request.form
        
        if not page_title or not page_content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写页面标题和内容'})

            return render_template('admin/simple_about_edit.html', 
                                 page_title=page_title, 
                                 page_content=page_content,
                                 meta_description=meta_description,
                                 meta_keywords=meta_keywords,
                                 is_active=is_active)
        
        try:
            # 查找或创建关于页面内容
            about_content = AboutContent.query.filter_by(section='main_content').first()
            if not about_content:
                about_content = AboutContent(
                    section='main_content',
                    title=page_title,
                    content=page_content,
                    order=0,
                    is_active=is_active
                )
                db.session.add(about_content)
            else:
                about_content.title = page_title
                about_content.content = page_content
                about_content.is_active = is_active
                about_content.updated_at = datetime.utcnow()
            
            # 保存SEO信息到其他内容块
            seo_content = AboutContent.query.filter_by(section='seo_info').first()
            if not seo_content:
                seo_content = AboutContent(
                    section='seo_info',
                    title='SEO信息',
                    content=f"description:{meta_description}\nkeywords:{meta_keywords}",
                    order=999,
                    is_active=False  # SEO信息不显示在页面上
                )
                db.session.add(seo_content)
            else:
                seo_content.content = f"description:{meta_description}\nkeywords:{meta_keywords}"
                seo_content.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '关于页面保存成功！'})

            return redirect(url_for('admin.admin_about'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '保存失败，请稍后重试'})

            print(f"保存关于页面错误: {e}")
    
    # GET请求，加载现有内容
    about_content = AboutContent.query.filter_by(section='main_content').first()
    seo_content = AboutContent.query.filter_by(section='seo_info').first()
    
    page_title = about_content.title if about_content else '关于我'
    page_content = about_content.content if about_content else ''
    is_active = about_content.is_active if about_content else True
    
    meta_description = ''
    meta_keywords = ''
    if seo_content and seo_content.content:
        content_parts = seo_content.content.split('\n')
        for part in content_parts:
            if part.startswith('description:'):
                meta_description = part.replace('description:', '')
            elif part.startswith('keywords:'):
                meta_keywords = part.replace('keywords:', '')
    
    return render_template('admin/simple_about_edit.html',
                         page_title=page_title,
                         page_content=page_content,
                         meta_description=meta_description,
                         meta_keywords=meta_keywords,
                         is_active=is_active) 