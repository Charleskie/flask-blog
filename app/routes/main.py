from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import Post, Project, Message, AboutContent, AboutContact, Version, Skill
from app.models.user import db
import re

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    # 获取最新的版本更新记录
    versions = Version.query.filter_by(is_active=True).order_by(Version.release_date.desc()).limit(5).all()
    
    # 获取技能数据
    skills = Skill.get_active_skills()
    
    return render_template('frontend/index.html', versions=versions, skills=skills)

@main_bp.route('/about')
def about():
    """关于页面"""
    # 获取关于页面内容
    contents = AboutContent.query.filter_by(is_active=True).order_by(AboutContent.order.asc()).all()
    contacts = AboutContact.query.filter_by(is_active=True).order_by(AboutContact.order.asc()).all()
    
    return render_template('frontend/about.html', contents=contents, contacts=contacts)

@main_bp.route('/projects')
def projects():
    """项目展示页面"""
    # 获取筛选参数
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    # 构建查询
    query = Project.query.filter_by(status='active')
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            db.or_(
                Project.title.contains(search),
                Project.description.contains(search),
                Project.short_description.contains(search)
            )
        )
    
    projects = query.order_by(Project.created_at.desc()).all()
    
    # 获取所有分类
    categories = db.session.query(Project.category).filter(
        Project.category.isnot(None), 
        Project.status == 'active'
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('frontend/projects.html', projects=projects, categories=categories, 
                         current_category=category, search=search)

@main_bp.route('/projects/<int:project_id>')
def project_detail(project_id):
    """项目详情页面"""
    project = Project.query.get_or_404(project_id)
    
    # 增加浏览次数
    project.view_count += 1
    db.session.commit()
    
    # 获取相关项目
    related_projects = Project.query.filter(
        Project.category == project.category,
        Project.id != project.id,
        Project.status == 'active'
    ).order_by(Project.created_at.desc()).limit(3).all()
    
    return render_template('frontend/project_detail.html', project=project, related_projects=related_projects)

@main_bp.route('/blog')
def blog():
    """博客页面"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    # 构建查询
    query = Post.query.filter_by(status='published')
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            db.or_(
                Post.title.contains(search),
                Post.content.contains(search),
                Post.excerpt.contains(search)
            )
        )
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 获取所有分类
    categories = db.session.query(Post.category).filter(
        Post.category.isnot(None), 
        Post.status == 'published'
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    # 获取热门文章（按浏览次数排序）
    popular_posts = Post.query.filter_by(status='published').order_by(
        Post.view_count.desc()
    ).limit(5).all()
    
    # 获取所有标签
    all_tags = []
    for post in Post.query.filter_by(status='published').all():
        if post.tags:
            all_tags.extend([tag.strip() for tag in post.tags.split(',')])
    
    # 统计标签出现次数
    from collections import Counter
    tag_counts = Counter(all_tags)
    popular_tags = tag_counts.most_common(10)  # 取前10个热门标签
    
    return render_template('frontend/blog.html', 
                         posts=posts, 
                         categories=categories, 
                         popular_posts=popular_posts,
                         popular_tags=popular_tags,
                         current_category=category, 
                         search=search)

@main_bp.route('/blog/post/<slug>')
def post_detail(slug):
    """文章详情页面"""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # 增加浏览次数
    post.view_count += 1
    db.session.commit()
    
    # 获取相关文章
    related_posts = Post.query.filter(
        Post.category == post.category,
        Post.id != post.id,
        Post.status == 'published'
    ).order_by(Post.created_at.desc()).limit(3).all()
    
    return render_template('frontend/post_detail.html', post=post, related_posts=related_posts)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """联系页面"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_text = request.form.get('message')
        
        # 验证输入
        if not name or not email or not subject or not message_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template('frontend/contact.html')
        
        # 验证邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请输入有效的邮箱地址'})

            return render_template('frontend/contact.html')
        
        try:
            # 创建新消息
            message = Message(
                name=name,
                email=email,
                subject=subject,
                message=message_text,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            db.session.add(message)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '消息发送成功！我们会尽快回复您。'})

            return redirect(url_for('main.contact'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '发送失败，请稍后重试'})

            print(f"保存消息错误: {e}")
    
    return render_template('frontend/contact.html')

@main_bp.route('/search')
def search():
    """全局搜索页面"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    results = {
        'posts': [],
        'projects': [],
        'total_count': 0
    }
    
    if query:
        # 搜索文章
        posts_query = Post.query.filter(
            db.or_(
                Post.title.contains(query),
                Post.content.contains(query),
                Post.excerpt.contains(query)
            ),
            Post.status == 'published'
        )
        
        posts = posts_query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=5, error_out=False
        )
        results['posts'] = posts
        
        # 搜索项目
        projects_query = Project.query.filter(
            db.or_(
                Project.title.contains(query),
                Project.description.contains(query),
                Project.short_description.contains(query)
            ),
            Project.status == 'active'
        )
        
        projects = projects_query.order_by(Project.created_at.desc()).limit(5).all()
        results['projects'] = projects
        
        # 计算总结果数
        results['total_count'] = posts.total + len(projects)
    
    return render_template('frontend/search.html', 
                         query=query, 
                         results=results,
                         current_page=page) 