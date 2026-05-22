from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, current_app
from flask_login import login_required, current_user
from app.models import Post, Message, MessageReply, AboutContent, AboutContact, Version, Skill, Link, VisitorStats, UserInteraction
from app.models.user import db
from app.utils.pdf_generator import generate_about_pdf
from app.utils.post_content import extract_post_plain_text
from collections import Counter
import re
import urllib.parse
from datetime import datetime, timezone
from email.utils import format_datetime
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


def _normalize_external_url(raw_url):
    """Normalize user-provided external URLs and default bare domains to HTTPS."""
    url = (raw_url or '').strip()
    if not url:
        return ''

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        url = f'https://{url.lstrip("/")}'

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        return ''

    normalized = urllib.parse.urlunparse((
        parsed.scheme.lower(),
        parsed.netloc,
        parsed.path or '',
        parsed.params or '',
        parsed.query or '',
        parsed.fragment or '',
    ))

    return normalized.rstrip('/') if parsed.path in ('', '/') and not parsed.query and not parsed.fragment else normalized


def _format_sitemap_lastmod(value):
    if not value:
        return None
    return value.date().isoformat()


def _normalize_tag_name(raw_tag):
    return re.sub(r'\s+', ' ', (raw_tag or '').strip())


def _normalize_series_name(raw_series):
    return Post.normalize_series(raw_series) or ''


def _build_tag_filter(tag_name):
    normalized_tag = _normalize_tag_name(tag_name)
    if not normalized_tag:
        return None

    return db.or_(
        Post.tags == normalized_tag,
        Post.tags.like(f'{normalized_tag},%'),
        Post.tags.like(f'{normalized_tag}, %'),
        Post.tags.like(f'%,{normalized_tag}'),
        Post.tags.like(f'%, {normalized_tag}'),
        Post.tags.like(f'%,{normalized_tag},%'),
        Post.tags.like(f'%, {normalized_tag},%'),
        Post.tags.like(f'%,{normalized_tag}, %'),
        Post.tags.like(f'%, {normalized_tag}, %')
    )


def _apply_post_filters(query, *, search='', category='', tag='', series=''):
    if search:
        query = query.filter(
            db.or_(
                Post.title.contains(search),
                Post.content.contains(search),
                Post.excerpt.contains(search),
                Post.tags.contains(search),
                Post.series.contains(search)
            )
        )

    if series:
        query = query.filter(Post.series == series)

    if tag:
        tag_filter = _build_tag_filter(tag)
        if tag_filter is not None:
            query = query.filter(tag_filter)

    if category:
        query = query.filter(Post.category == category)

    return query


def _collect_blog_facets(posts):
    category_counter = Counter()
    series_counter = Counter()
    tag_counter = Counter()

    for post in posts:
        if post.category:
            category_counter[post.category] += 1
        if post.series:
            series_counter[post.series] += 1
        for tag in post.get_tags_list():
            tag_counter[tag] += 1

    categories = sorted(category_counter.keys())
    series_groups = sorted(
        series_counter.items(),
        key=lambda item: (-item[1], item[0].lower())
    )
    popular_tags = sorted(
        tag_counter.items(),
        key=lambda item: (-item[1], item[0].lower())
    )[:12]

    return categories, dict(category_counter), series_groups, popular_tags


def _build_blog_page_copy(*, current_view='all', current_tag='', current_series='', current_category='', total=0):
    if current_series:
        prefix = '你收藏的这个系列' if current_view == 'favorites' else '这个系列'
        return f'{prefix}按发布时间整理展示，当前共 {total} 篇文章。'
    if current_tag:
        prefix = '你收藏的相关文章' if current_view == 'favorites' else '使用这个标签的文章'
        return f'{prefix}当前共 {total} 篇，方便顺着同一主题继续读。'
    if current_category:
        prefix = '当前分类下你收藏的文章' if current_view == 'favorites' else '当前分类下的文章'
        return f'{prefix}共 {total} 篇，按时间倒序展示。'
    if current_view == 'favorites':
        return f'这里汇总你收藏过的文章，当前共 {total} 篇。'
    return f'按时间排序展示，当前共 {total} 篇文章。'


def _resolve_blog_heading(*, current_view='all', current_tag='', current_series='', current_category=''):
    if current_series:
        return f'{current_series} 系列'
    if current_tag:
        return f'#{current_tag}'
    if current_category:
        return current_category
    if current_view == 'favorites':
        return '我的收藏'
    return '最新文章'


def _get_related_posts(post, limit=3):
    post_tags = set(post.get_tags_list())
    scored_posts = []

    for candidate in Post.query.filter(
        Post.status == 'published',
        Post.id != post.id
    ).all():
        score = 0
        shared_tags = post_tags.intersection(candidate.get_tags_list())

        if post.series and candidate.series == post.series:
            score += 6
        if post.category and candidate.category == post.category:
            score += 2
        score += len(shared_tags) * 2

        if score > 0:
            scored_posts.append((
                score,
                len(shared_tags),
                candidate.updated_at or candidate.created_at,
                candidate
            ))

    scored_posts.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    related_posts = [item[3] for item in scored_posts[:limit]]

    if len(related_posts) < limit:
        existing_ids = {item.id for item in related_posts}
        fallback_posts = Post.query.filter(
            Post.status == 'published',
            Post.id != post.id,
            Post.id.notin_(existing_ids or {-1})
        ).order_by(Post.created_at.desc()).limit(limit - len(related_posts)).all()
        related_posts.extend(fallback_posts)

    return related_posts


def _get_adjacent_posts(post):
    ordered_query = Post.query.filter(Post.status == 'published')
    if post.series:
        ordered_query = ordered_query.filter(Post.series == post.series)

    ordered_posts = ordered_query.order_by(Post.created_at.asc(), Post.id.asc()).all()
    previous_post = None
    next_post = None
    current_index = None

    for index, item in enumerate(ordered_posts):
        if item.id != post.id:
            continue
        current_index = index
        previous_post = ordered_posts[index - 1] if index > 0 else None
        next_post = ordered_posts[index + 1] if index + 1 < len(ordered_posts) else None
        break

    return previous_post, next_post, ordered_posts, current_index


def _format_rss_pubdate(value):
    if not value:
        value = datetime.utcnow()
    return format_datetime(value.replace(tzinfo=timezone.utc))


def _build_rss_description(post, max_length=220):
    source_text = post.excerpt if post.excerpt else post.content
    plain_text = extract_post_plain_text(source_text, post.normalized_content_format)
    plain_text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', plain_text)
    plain_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain_text)
    plain_text = re.sub(r'`([^`]+)`', r'\1', plain_text)
    plain_text = re.sub(r'(^|\s)#{1,6}\s*', ' ', plain_text)
    plain_text = re.sub(r'(^|\s)&gt;\s*', ' ', plain_text)
    plain_text = re.sub(r'(^|\s)>\s*', ' ', plain_text)
    plain_text = re.sub(r'[*_~]+', '', plain_text)
    plain_text = plain_text.replace('#', ' ')
    plain_text = plain_text.replace('>', ' ')
    plain_text = plain_text.replace('`', '')
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()
    if len(plain_text) <= max_length:
        return plain_text
    return plain_text[:max_length].rstrip() + '...'


def _get_blog_feed_meta(category='', tag='', series=''):
    if series:
        return {
            'title': f'{series} 系列 - Kim\'s Blog',
            'description': f'按发布时间整理的「{series}」系列文章订阅。',
            'scope_label': f'系列：{series}',
            'scope_kind': 'series',
        }
    if tag:
        return {
            'title': f'#{tag} - Kim\'s Blog',
            'description': f'带有「{tag}」标签的文章订阅。',
            'scope_label': f'标签：#{tag}',
            'scope_kind': 'tag',
        }
    if category:
        return {
            'title': f'{category} - Kim\'s Blog',
            'description': f'分类「{category}」下的最新文章订阅。',
            'scope_label': f'分类：{category}',
            'scope_kind': 'category',
        }
    return {
        'title': 'Kim\'s Blog RSS',
        'description': 'Kim\'s Blog 最新公开文章订阅。',
        'scope_label': '全部文章',
        'scope_kind': 'all',
    }


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

        normalized_url = _normalize_external_url(data.get('url', ''))
        if not normalized_url:
            return jsonify({'success': False, 'message': '请输入有效的网站链接'}), 400
        
        # 检查是否已存在相同的友链申请
        existing_link = Link.query.filter_by(
            name=data.get('name').strip(),
            url=normalized_url
        ).first()
        
        if existing_link:
            return jsonify({'success': False, 'message': '该友链已存在，请勿重复申请'}), 400
        
        # 创建友链申请
        link = Link(
            name=data.get('name').strip(),
            url=normalized_url,
            description=(data.get('description', '') or '').strip(),
            email=(data.get('email', '') or '').strip(),
            status='pending'  # 待审核状态
        )
        
        db.session.add(link)
        db.session.flush()  # 获取ID
        
        # 创建消息通知给管理员
        from app.models import Message, Notification
        message = Message(
            name=data.get('name', '友链申请'),
            email=(data.get('email', '') or '').strip(),
            subject=f'友链申请：{data.get("name")}',
            message=f'网站名称：{data.get("name")}\n网站链接：{normalized_url}\n网站描述：{data.get("description", "无")}\n联系邮箱：{data.get("email", "无")}',
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

def _render_blog_page(forced_tag=None, forced_series=None):
    page = request.args.get('page', 1, type=int)
    category = (request.args.get('category', '') or '').strip()
    search = (request.args.get('search', '') or '').strip()
    view = (request.args.get('view', 'all') or 'all').strip().lower()
    current_tag = _normalize_tag_name(forced_tag if forced_tag is not None else request.args.get('tag', ''))
    current_series = _normalize_series_name(forced_series if forced_series is not None else request.args.get('series', ''))

    if view not in {'all', 'favorites'}:
        view = 'all'

    all_published_query = Post.query.filter_by(status='published')
    published_posts_total = all_published_query.count()

    favorite_post_ids = set()
    favorite_posts_query = all_published_query.filter(Post.id == -1)
    favorite_posts_total = 0

    if current_user.is_authenticated:
        favorite_posts_query = all_published_query.join(
            UserInteraction,
            db.and_(
                UserInteraction.content_id == Post.id,
                UserInteraction.type == 1,
                UserInteraction.user_id == current_user.id,
                UserInteraction.favorite == 1
            )
        )
        favorite_post_ids = {
            post_id for post_id, in favorite_posts_query.with_entities(Post.id).all()
        }
        favorite_posts_total = len(favorite_post_ids)

    base_query = (
        favorite_posts_query
        if view == 'favorites' and current_user.is_authenticated
        else all_published_query.filter(Post.id == -1)
        if view == 'favorites'
        else all_published_query
    )

    facet_query = _apply_post_filters(base_query, search=search)
    facet_posts = facet_query.order_by(Post.created_at.desc()).all()
    available_posts_total = len(facet_posts)
    categories, category_count, series_groups, popular_tags = _collect_blog_facets(facet_posts)

    filtered_query = _apply_post_filters(
        base_query,
        search=search,
        category=category,
        tag=current_tag,
        series=current_series
    )
    posts = filtered_query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    popular_posts = filtered_query.order_by(Post.view_count.desc()).limit(5).all()
    if not popular_posts:
        popular_posts = all_published_query.order_by(Post.view_count.desc()).limit(5).all()

    page_heading = _resolve_blog_heading(
        current_view=view,
        current_tag=current_tag,
        current_series=current_series,
        current_category=category
    )
    if view == 'favorites' and not current_user.is_authenticated:
        page_copy = '登录后即可查看你收藏过的文章。'
    else:
        page_copy = _build_blog_page_copy(
            current_view=view,
            current_tag=current_tag,
            current_series=current_series,
            current_category=category,
            total=posts.total
        )

    return render_template(
        'frontend/blog.html',
        posts=posts,
        categories=categories,
        category_count=category_count,
        popular_posts=popular_posts,
        popular_tags=popular_tags,
        series_groups=series_groups,
        current_category=category,
        current_tag=current_tag,
        current_series=current_series,
        search=search,
        current_view=view,
        page_heading=page_heading,
        page_copy=page_copy,
        available_posts_total=available_posts_total,
        published_posts_total=published_posts_total,
        favorite_posts_total=favorite_posts_total,
        favorite_post_ids=favorite_post_ids
    )


@main_bp.route('/blog')
def blog():
    """博客页面"""
    return _render_blog_page()


@main_bp.route('/blog/tag/<path:tag_name>')
def blog_tag(tag_name):
    """标签文章列表页。"""
    return _render_blog_page(forced_tag=tag_name)


@main_bp.route('/blog/series/<path:series_name>')
def blog_series(series_name):
    """系列文章列表页。"""
    return _render_blog_page(forced_series=series_name)


@main_bp.route('/blog/subscribe')
def blog_subscribe():
    """博客订阅说明页。"""
    category = (request.args.get('category', '') or '').strip()
    tag = _normalize_tag_name(request.args.get('tag', ''))
    series = _normalize_series_name(request.args.get('series', ''))

    all_published_posts = Post.query.filter_by(status='published').all()
    categories, category_count, series_groups, _ = _collect_blog_facets(all_published_posts)
    published_total = len(all_published_posts)
    feed_query = _apply_post_filters(
        Post.query.filter_by(status='published'),
        category=category,
        tag=tag,
        series=series
    )
    latest_posts = feed_query.order_by(Post.created_at.desc()).limit(6).all()

    feed_url = url_for(
        'main.blog_rss',
        category=category or None,
        tag=tag or None,
        series=series or None,
        _external=True
    )
    reader_apps = [
        {'label': 'Follow', 'url': 'https://follow.is/'},
        {'label': 'Feedly', 'url': 'https://feedly.com/homepage'},
        {'label': 'Inoreader', 'url': 'https://www.inoreader.com/'},
        {'label': 'NetNewsWire', 'url': 'https://netnewswire.com/'},
    ]

    scope_groups = [
        {
            'title': '常用范围',
            'options': [
                {
                    'label': '全部文章',
                    'description': f'订阅博客的所有公开文章更新，当前共 {published_total} 篇。',
                    'url': url_for('main.blog_subscribe'),
                    'is_current': not any([category, tag, series]),
                }
            ]
        }
    ]

    category_options = [
        {
            'label': category_name,
            'description': f'只跟进当前分类下的新文章，当前共 {category_count.get(category_name, 0)} 篇。',
            'url': url_for('main.blog_subscribe', category=category_name),
            'is_current': category == category_name and not series and not tag,
        }
        for category_name in categories
    ]
    if category and not any(option['label'] == category for option in category_options):
        category_options.insert(0, {
            'label': category,
            'description': f'只跟进当前分类下的新文章，当前共 {category_count.get(category, 0)} 篇。',
            'url': url_for('main.blog_subscribe', category=category),
            'is_current': True,
        })
    if category_options:
        scope_groups.append({
            'title': '按分类订阅',
            'options': category_options,
        })

    series_options_list = [
        {
            'label': f'{series_name} 系列',
            'description': f'只跟进这个系列的后续文章，当前共 {count} 篇。',
            'url': url_for('main.blog_subscribe', series=series_name),
            'is_current': series == _normalize_series_name(series_name),
        }
        for series_name, count in series_groups
    ]
    if series and not any(_normalize_series_name(option['label'].removesuffix(' 系列')) == series for option in series_options_list):
        series_count = sum(1 for post in all_published_posts if _normalize_series_name(post.series) == series)
        series_options_list.insert(0, {
            'label': f'{series} 系列',
            'description': f'只跟进这个系列的后续文章，当前共 {series_count} 篇。',
            'url': url_for('main.blog_subscribe', series=series),
            'is_current': True,
        })
    if series_options_list:
        scope_groups.append({
            'title': '按系列订阅',
            'options': series_options_list,
        })

    tag_options = []
    if tag:
        tag_count = sum(1 for post in all_published_posts if tag in post.get_tags_list())
        tag_options.append({
            'label': f'#{tag}',
            'description': f'只跟进带有这个标签的文章，当前共 {tag_count} 篇。',
            'url': url_for('main.blog_subscribe', tag=tag),
            'is_current': True,
        })
    if tag_options:
        scope_groups.append({
            'title': '当前标签',
            'options': tag_options,
        })

    return render_template(
        'frontend/blog_subscribe.html',
        feed_url=feed_url,
        reader_apps=reader_apps,
        latest_posts=latest_posts,
        scope_groups=scope_groups,
        current_category=category,
        current_tag=tag,
        current_series=series,
    )


@main_bp.route('/blog/rss.xml')
def blog_rss():
    """博客 RSS 订阅源。"""
    category = (request.args.get('category', '') or '').strip()
    tag = _normalize_tag_name(request.args.get('tag', ''))
    series = _normalize_series_name(request.args.get('series', ''))

    feed_query = _apply_post_filters(
        Post.query.filter_by(status='published'),
        category=category,
        tag=tag,
        series=series
    )
    posts = feed_query.order_by(Post.created_at.desc()).limit(20).all()
    feed_meta = _get_blog_feed_meta(category=category, tag=tag, series=series)
    feed_title = feed_meta['title']
    feed_description = feed_meta['description']

    feed_url = url_for('main.blog_rss', category=category or None, tag=tag or None, series=series or None, _external=True)
    blog_url = url_for('main.blog', _external=True)
    last_build_date = _format_rss_pubdate(posts[0].updated_at if posts else datetime.utcnow())

    items = []
    for post in posts:
        post_url = url_for('main.post_detail', slug=post.safe_slug, _external=True)
        description = escape(_build_rss_description(post))
        pub_date = _format_rss_pubdate(post.updated_at or post.created_at)
        items.append(
            f"""<item>
    <title>{escape(post.title)}</title>
    <link>{escape(post_url)}</link>
    <guid>{escape(post_url)}</guid>
    <pubDate>{pub_date}</pubDate>
    <description>{description}</description>
</item>"""
        )

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>{escape(feed_title)}</title>
    <link>{escape(blog_url)}</link>
    <description>{escape(feed_description)}</description>
    <language>zh-CN</language>
    <lastBuildDate>{last_build_date}</lastBuildDate>
    <atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml" />
    {''.join(items)}
</channel>
</rss>"""

    response = make_response(rss_xml)
    response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return response

@main_bp.route('/blog/post/<slug>')
def post_detail(slug):
    """文章详情页面"""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # 增加浏览次数
    post.view_count += 1
    db.session.commit()

    related_posts = _get_related_posts(post)
    previous_post, next_post, series_posts, series_index = _get_adjacent_posts(post)
    subscribe_page_url = url_for(
        'main.blog_subscribe',
        series=post.series or None,
        category=post.category if not post.series else None,
        _external=True
    )

    return render_template(
        'frontend/post_detail.html',
        post=post,
        related_posts=related_posts,
        previous_post=previous_post,
        next_post=next_post,
        series_posts=series_posts if post.series else [],
        series_index=series_index,
        subscribe_page_url=subscribe_page_url
    )

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
