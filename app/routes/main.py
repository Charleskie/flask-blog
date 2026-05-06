from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, current_app
from flask_login import login_required, current_user
from app.models import Post, Message, MessageReply, AboutContent, AboutContact, Version, Skill, Link, VisitorStats
from app.models.user import db
from app.utils.pdf_generator import generate_about_pdf
import re
import urllib.parse
from datetime import datetime
from xml.sax.saxutils import escape


main_bp = Blueprint('main', __name__)


def _get_public_site_root():
    """Return the canonical public site root for crawlable files."""
    configured_site_url = (
        current_app.config.get('SITE_URL')
        or current_app.config.get('PUBLIC_SITE_URL')
        or ''
    ).strip()

    if configured_site_url:
        return configured_site_url.rstrip('/') + '/'

    return request.url_root.rstrip('/') + '/'


def _absolute_public_url(path):
    path = path.lstrip('/')
    return urllib.parse.urljoin(_get_public_site_root(), path)


def _format_sitemap_lastmod(value):
    if not value:
        return None
    return value.date().isoformat()


def _get_contact_page_context():
    """Build a consistent contact page context with admin-managed channels first."""
    managed_channels = [
        item.to_dict()
        for item in AboutContact.query.filter_by(is_active=True)
        .order_by(AboutContact.order.asc(), AboutContact.id.asc())
        .all()
    ]

    default_channels = [
        {
            'platform': '邮箱',
            'icon': 'fas fa-envelope',
            'url': 'mailto:wdws851421092@gmail.com',
            'text': 'wdws851421092@gmail.com',
            'color': 'primary',
        },
        {
            'platform': 'GitHub',
            'icon': 'fab fa-github',
            'url': 'https://github.com/Charleskie',
            'text': 'Charleskie',
            'color': 'dark',
        },
        {
            'platform': '办公地点',
            'icon': 'fas fa-location-dot',
            'url': '',
            'text': '深圳，中国',
            'color': 'secondary',
        },
        {
            'platform': '在线时间',
            'icon': 'fas fa-clock',
            'url': '',
            'text': '周一至周五 9:00-18:00',
            'color': 'secondary',
        },
    ]

    contact_channels = managed_channels or default_channels

    def _match_channel(keywords):
        for item in contact_channels:
            haystack = ' '.join(
                str(item.get(part, '') or '')
                for part in ('platform', 'icon', 'text', 'url')
            ).lower()
            if any(keyword in haystack for keyword in keywords):
                return item
        return None

    email_contact = _match_channel(['mail', '邮箱', 'email']) or default_channels[0]
    phone_contact = _match_channel(['phone', '电话', 'mobile', '热线'])
    location_contact = _match_channel(['location', 'map', '地址', '地点', '城市'])

    office_locations = [
        {
            'name': '深圳 - 南山高新园',
            'address': (location_contact or {}).get('text') or '深圳市南山区高新南一道',
            'lat': 22.5405,
            'lng': 113.9344,
            'phone': (phone_contact or {}).get('text') or '+86 135 **** 8704',
            'email': (email_contact or {}).get('text') or 'wdws851421092@gmail.com',
            'workingHours': '工作时间：周一至周五 9:00-18:00',
        }
    ]

    faq_items = [
        {
            'id': 'faq-reply',
            'question': '消息多久能收到回复？',
            'answer': '工作日通常会在 24 小时内回复；如果是账号或内容相关的问题，登录后留言也更方便我回溯上下文。',
        },
        {
            'id': 'faq-scope',
            'question': '这页适合提交哪些内容？',
            'answer': '合作邀约、网站建议、内容纠错、功能反馈都可以直接发；如果你想申请友链，建议在友链页面提交会更高效。',
        },
    ]

    link_contacts = [item for item in contact_channels if item.get('url')]

    return {
        'contact_channels': contact_channels,
        'link_contacts': link_contacts[:4],
        'office_locations': office_locations,
        'faq_items': faq_items,
    }


def _get_contact_view_context(selected_message_id=None, compose_mode=False):
    """Build contact page context with per-user conversation state."""
    context = _get_contact_page_context()
    user_messages = []
    selected_message = None
    show_conversation_inbox = False
    selected_message_has_admin_reply = False
    user_unread_total = 0

    if current_user.is_authenticated:
        user_messages = Message.visible_to_user_query(current_user.email).order_by(Message.created_at.desc()).all()
        show_conversation_inbox = compose_mode or len(user_messages) > 0

        if show_conversation_inbox and not compose_mode:
            if selected_message_id:
                selected_message = next(
                    (message for message in user_messages if message.id == selected_message_id),
                    None
                )
            if selected_message is None:
                selected_message = user_messages[0]
            if selected_message is not None:
                if selected_message.has_unread_for_user():
                    selected_message.mark_as_read_by_user()
                    db.session.commit()
                selected_message_has_admin_reply = any(
                    reply.reply_type == 'admin' for reply in selected_message.replies
                )

        user_unread_total = sum(
            1
            for message in user_messages
            if message.has_unread_for_user()
        )

    context.update({
        'user_messages': user_messages,
        'selected_message': selected_message,
        'show_conversation_inbox': show_conversation_inbox,
        'compose_mode': compose_mode,
        'selected_message_has_admin_reply': selected_message_has_admin_reply,
        'selected_message_can_follow_up': selected_message is not None,
        'user_unread_total': user_unread_total,
    })
    return context


@main_bp.route('/messages')
@login_required
def message_center():
    """统一消息中心入口。"""
    if current_user.is_admin:
        return redirect(url_for('admin.admin_messages'))

    has_messages = Message.visible_to_user_query(current_user.email).count() > 0
    if has_messages:
        return redirect(url_for('main.contact'))

    return redirect(url_for('main.contact', mode='new'))


@main_bp.route('/robots.txt')
def robots_txt():
    """Expose crawler rules and advertise the XML sitemap."""
    sitemap_url = _absolute_public_url('/sitemap.xml')
    content = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin',
        'Disallow: /api/',
        'Disallow: /login',
        'Disallow: /register',
        'Disallow: /settings',
        'Disallow: /messages',
        '',
        f'Sitemap: {sitemap_url}',
        '',
    ])
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@main_bp.route('/sitemap.xml')
def sitemap_xml():
    """Generate an XML sitemap for public pages and published blog posts."""
    static_pages = [
        {'loc': _absolute_public_url('/'), 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': _absolute_public_url('/blog'), 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': _absolute_public_url('/about'), 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': _absolute_public_url('/links'), 'priority': '0.6', 'changefreq': 'weekly'},
        {'loc': _absolute_public_url('/contact'), 'priority': '0.5', 'changefreq': 'monthly'},
    ]

    posts = Post.query.filter_by(status='published').order_by(Post.updated_at.desc()).all()
    for post in posts:
        static_pages.append({
            'loc': _absolute_public_url(url_for('main.post_detail', slug=post.safe_slug)),
            'lastmod': _format_sitemap_lastmod(post.updated_at or post.created_at),
            'priority': '0.8',
            'changefreq': 'monthly',
        })

    url_blocks = []
    for page in static_pages:
        lines = [
            '  <url>',
            f'    <loc>{escape(page["loc"])}</loc>',
        ]
        if page.get('lastmod'):
            lines.append(f'    <lastmod>{page["lastmod"]}</lastmod>')
        if page.get('changefreq'):
            lines.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        if page.get('priority'):
            lines.append(f'    <priority>{page["priority"]}</priority>')
        lines.append('  </url>')
        url_blocks.append('\n'.join(lines))

    content = '\n'.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        *url_blocks,
        '</urlset>',
        '',
    ])

    response = make_response(content)
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response

@main_bp.route('/')
def index():
    """首页"""
    versions = Version.query.filter_by(is_active=True).order_by(Version.release_date.desc()).limit(5).all()
    latest_version = versions[0] if versions else None

    skills = Skill.get_active_skills()
    skill_groups = {}
    for skill in skills:
        category = skill.category or '其他'
        skill_groups.setdefault(category, []).append(skill)
    skill_groups = list(skill_groups.items())[:4]

    recent_posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).limit(6).all()
    popular_posts = Post.query.filter_by(status='published').order_by(
        Post.view_count.desc(), Post.created_at.desc()
    ).limit(4).all()

    featured_links = Link.get_featured_links()[:4]
    if not featured_links:
        featured_links = Link.get_active_links()[:4]

    about_content = AboutContent.query.filter_by(section='main_content', is_active=True).first()
    about_excerpt = ''
    if about_content and about_content.content:
        about_excerpt = re.sub(r'<[^>]+>', ' ', about_content.content)
        about_excerpt = re.sub(r'\s+', ' ', about_excerpt).strip()
        about_excerpt = about_excerpt[:140] + ('...' if len(about_excerpt) > 140 else '')

    top_categories = db.session.query(
        Post.category,
        db.func.count(Post.id).label('count')
    ).filter(
        Post.status == 'published',
        Post.category.isnot(None)
    ).group_by(Post.category).order_by(
        db.func.count(Post.id).desc(),
        Post.category.asc()
    ).limit(5).all()

    stats = {
        'post_count': Post.query.filter_by(status='published').count(),
        'skill_count': len(skills),
        'link_count': Link.query.filter_by(status='active').count(),
        'version_count': Version.query.filter_by(is_active=True).count()
    }

    return render_template(
        'frontend/index.html',
        versions=versions,
        latest_version=latest_version,
        skills=skills,
        skill_groups=skill_groups,
        recent_posts=recent_posts,
        popular_posts=popular_posts,
        featured_links=featured_links,
        about_excerpt=about_excerpt,
        top_categories=top_categories,
        stats=stats
    )

@main_bp.route('/about')
def about():
    """关于页面"""
    # 获取关于页面主内容
    about_content = AboutContent.query.filter_by(section='main_content', is_active=True).first()
    
    page_title = about_content.title if about_content else '关于我'
    page_content = about_content.content if about_content else ''
    
    return render_template('frontend/about.html', page_title=page_title, page_content=page_content)

@main_bp.route('/about/pdf')
def about_pdf():
    """关于页面PDF下载"""
    try:
        # 获取关于页面主内容
        about_content = AboutContent.query.filter_by(section='main_content', is_active=True).first()
        
        page_title = about_content.title if about_content else '关于我'
        page_content = about_content.content if about_content else ''
        
        # 如果没有内容，返回错误
        if not page_content:
            return jsonify({'error': '暂无内容可生成PDF'}), 404
        
        # 生成PDF
        pdf_bytes = generate_about_pdf(
            page_title=page_title,
            page_content=page_content,
            base_url=request.url_root
        )
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 使用英文文件名避免编码问题
        filename = f"about_{timestamp}.pdf"
        # 如果有中文标题，也生成一个中文文件名用于显示
        display_filename = f"{page_title}_{timestamp}.pdf" if page_title else filename
        
        # 创建响应
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        
        # 使用RFC 5987标准处理中文文件名
        encoded_filename = urllib.parse.quote(display_filename.encode('utf-8'))
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
        response.headers['Content-Length'] = len(pdf_bytes)
        
        return response
        
    except Exception as e:
        print(f"生成PDF错误: {e}")
        return jsonify({'error': 'PDF生成失败，请稍后重试'}), 500

@main_bp.route('/api/apply-link', methods=['POST'])
def apply_link():
    """申请友链API"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name') or not data.get('url'):
            return jsonify({'success': False, 'message': '网站名称和链接为必填项'}), 400
        
        # 验证URL格式
        import re
        url_pattern = r'^https?://.+'
        if not re.match(url_pattern, data.get('url', '')):
            return jsonify({'success': False, 'message': '请输入有效的网站链接'}), 400
        
        # 检查是否已存在相同的友链申请
        existing_link = Link.query.filter_by(
            name=data.get('name'),
            url=data.get('url')
        ).first()
        
        if existing_link:
            return jsonify({'success': False, 'message': '该友链已存在，请勿重复申请'}), 400
        
        # 创建友链申请
        link = Link(
            name=data.get('name'),
            url=data.get('url'),
            description=data.get('description', ''),
            email=data.get('email', ''),
            status='pending'  # 待审核状态
        )
        
        db.session.add(link)
        db.session.flush()  # 获取ID
        
        # 创建消息通知给管理员
        from app.models import Message, Notification
        message = Message(
            name=data.get('name', '友链申请'),
            email=data.get('email', ''),
            subject=f'友链申请：{data.get("name")}',
            message=f'网站名称：{data.get("name")}\n网站链接：{data.get("url")}\n网站描述：{data.get("description", "无")}\n联系邮箱：{data.get("email", "无")}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(message)
        db.session.flush()
        
        # 创建通知
        notification = Message.create_message_notification(message)
        if notification:
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '申请提交成功，我们会尽快审核'})
        
    except Exception as e:
        db.session.rollback()
        print(f"申请友链失败: {e}")
        return jsonify({'success': False, 'message': '申请提交失败，请稍后重试'}), 500

@main_bp.route('/api/visitor-stats', methods=['GET'])
def get_visitor_stats():
    """获取访问量统计API"""
    try:
        # 获取总统计数据
        total_stats = VisitorStats.get_total_stats()
        
        # 获取今日统计数据
        today_stats = VisitorStats.get_today_stats()
        
        # 获取最近7天统计数据
        recent_stats = VisitorStats.get_recent_stats(7)
        
        return jsonify({
            'success': True,
            'data': {
                'total_views': total_stats['total_views'],
                'total_visitors': total_stats['total_visitors'],
                'today_views': today_stats.page_views,
                'today_visitors': today_stats.unique_visitors,
                'recent_stats': [
                    {
                        'date': stat.date.isoformat(),
                        'page_views': stat.page_views,
                        'unique_visitors': stat.unique_visitors
                    } for stat in recent_stats
                ]
            }
        })
    except Exception as e:
        print(f"获取访问量统计失败: {e}")
        return jsonify({'success': False, 'message': '获取统计数据失败'}), 500

@main_bp.route('/api/track-visit', methods=['POST'])
def track_visit():
    """记录访问API"""
    try:
        data = request.get_json() or {}
        is_unique = data.get('unique', False)
        
        # 增加页面浏览量
        stats = VisitorStats.increment_page_view()
        
        # 如果是独立访客，增加独立访客数
        if is_unique:
            stats = VisitorStats.increment_unique_visitor()
        
        return jsonify({
            'success': True,
            'data': {
                'today_views': stats.page_views,
                'today_visitors': stats.unique_visitors
            }
        })
    except Exception as e:
        print(f"记录访问失败: {e}")
        return jsonify({'success': False, 'message': '记录访问失败'}), 500

@main_bp.route('/links')
def links():
    """友链页面"""
    # 获取所有活跃的友链
    links = Link.get_active_links()
    
    # 获取推荐的友链
    featured_links = Link.get_featured_links()
    
    return render_template('frontend/links.html', links=links, featured_links=featured_links)

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
    selected_message_id = request.args.get('message_id', type=int)
    compose_mode = request.args.get('mode') == 'new'

    if request.method == 'POST':
        selected_message_id = request.form.get('message_id', type=int) or selected_message_id
        conversation_action = (request.form.get('conversation_action') or '').strip()
        follow_up_mode = conversation_action == 'follow_up'
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_text = request.form.get('message')

        if follow_up_mode:
            if not current_user.is_authenticated or not selected_message_id:
                error_message = '当前会话不可用，请刷新后重试'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': error_message})

                return render_template(
                    'frontend/contact.html',
                    **_get_contact_view_context(selected_message_id=selected_message_id, compose_mode=False)
                )

            parent_message = Message.visible_to_user_query(current_user.email).filter_by(
                id=selected_message_id
            ).first()

            if not parent_message:
                error_message = '没有找到这段对话'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': error_message})

                return render_template(
                    'frontend/contact.html',
                    **_get_contact_view_context(selected_message_id=selected_message_id, compose_mode=False)
                )

            if not message_text:
                error_message = '请输入要补充的消息内容'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': error_message})

                return render_template(
                    'frontend/contact.html',
                    **_get_contact_view_context(selected_message_id=parent_message.id, compose_mode=False)
                )

            try:
                reply_record = MessageReply.create_reply(
                    message_id=parent_message.id,
                    reply_content=message_text,
                    reply_type='user',
                    sender_name=current_user.get_display_name(),
                    sender_email=current_user.email
                )

                db.session.add(reply_record)

                has_admin_reply = any(
                    reply.reply_type == 'admin' for reply in parent_message.replies
                )
                parent_message.restore_for_admin()
                if has_admin_reply:
                    parent_message.status = 'in_conversation'
                else:
                    parent_message.status = 'unread'
                    parent_message.read_at = None

                from app.models import Notification, User
                admin_user = User.query.filter_by(is_admin=True).order_by(User.id.asc()).first()
                if admin_user:
                    notification = Notification(
                        user_id=admin_user.id,
                        type='message',
                        title=f'{current_user.get_display_name()} 补充了私信',
                        content=f'"{message_text[:100]}{"..." if len(message_text) > 100 else ""}"',
                        related_id=parent_message.id,
                        related_type='message',
                        related_url=f'/admin/messages?message_id={parent_message.id}',
                        sender_id=current_user.id,
                        sender_name=current_user.get_display_name()
                    )
                    db.session.add(notification)

                db.session.commit()

                redirect_url = url_for('main.contact', message_id=parent_message.id)
                success_message = '补充消息已发送，已加入当前对话。'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': success_message,
                        'redirect_url': redirect_url
                    })

                return redirect(redirect_url)

            except Exception as e:
                db.session.rollback()
                print(f"追加消息错误: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '发送失败，请稍后重试'})

                return render_template(
                    'frontend/contact.html',
                    **_get_contact_view_context(selected_message_id=parent_message.id, compose_mode=False)
                )
        
        # 验证输入
        if not name or not email or not subject or not message_text:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请填写所有必填字段'})

            return render_template(
                'frontend/contact.html',
                **_get_contact_view_context(selected_message_id=selected_message_id, compose_mode=True)
            )
        
        # 验证邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '请输入有效的邮箱地址'})

            return render_template(
                'frontend/contact.html',
                **_get_contact_view_context(selected_message_id=selected_message_id, compose_mode=True)
            )
        
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
            db.session.flush()  # 获取消息ID
            
            # 创建消息通知
            notification = Message.create_message_notification(message)
            if notification:
                db.session.add(notification)
            
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                redirect_url = url_for('main.contact', message_id=message.id) if current_user.is_authenticated else url_for('main.contact')
                return jsonify({
                    'success': True,
                    'message': '消息发送成功！我们会尽快回复您。',
                    'redirect_url': redirect_url
                })

            if current_user.is_authenticated:
                return redirect(url_for('main.contact', message_id=message.id))

            return redirect(url_for('main.contact'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '发送失败，请稍后重试'})

            print(f"保存消息错误: {e}")
    
    return render_template(
        'frontend/contact.html',
        **_get_contact_view_context(selected_message_id=selected_message_id, compose_mode=compose_mode)
    )

@main_bp.route('/contact/messages')
@login_required
def contact_messages():
    """用户查看私信记录"""
    return redirect(url_for('main.contact'))

@main_bp.route('/contact/messages/<int:message_id>')
@login_required
def contact_message_detail(message_id):
    """用户查看私信详情"""
    Message.visible_to_user_query(current_user.email).filter_by(id=message_id).first_or_404()
    return redirect(url_for('main.contact', message_id=message_id))

@main_bp.route('/contact/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_contact_message(message_id):
    """用户侧单方删除会话。"""
    message = Message.visible_to_user_query(current_user.email).filter_by(id=message_id).first_or_404()

    try:
        message.hide_for_user()

        purged = False
        if message.can_purge():
            message.purge_related_records()
            purged = True

        db.session.commit()

        redirect_url = url_for('main.contact')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': '对话已从你的会话列表移除',
                'redirect_url': redirect_url,
                'purged': purged
            })

        return redirect(redirect_url)
    except Exception as e:
        db.session.rollback()
        print(f"用户删除会话失败: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
        return redirect(url_for('main.contact', message_id=message_id))

@main_bp.route('/search')
def search():
    """全局搜索页面"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    results = {
        'posts': [],
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
        
        # 计算总结果数
        results['total_count'] = posts.total
    
    return render_template('frontend/search.html', 
                         query=query, 
                         results=results,
                         current_page=page) 
