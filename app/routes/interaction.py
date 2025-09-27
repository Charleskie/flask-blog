import random

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import db
from app.models import Post, Project, Comment, CommentReply, UserInteraction, CommentLike, Notification
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
import pytz

interaction_bp = Blueprint('interaction', __name__)

def to_china_time(utc_time):
    """将UTC时间转换为中国时区时间"""
    if utc_time is None:
        return None
    
    # 确保时间是UTC时区
    if utc_time.tzinfo is None:
        utc_time = pytz.utc.localize(utc_time)
    
    # 转换为中国时区
    china_tz = pytz.timezone('Asia/Shanghai')
    china_time = utc_time.astimezone(china_tz)
    
    return china_time.strftime('%Y-%m-%d %H:%M')

@interaction_bp.route('/test', methods=['GET'])
def test_api():
    """测试API是否正常工作"""
    return jsonify({'success': True, 'message': 'API正常工作'})

@interaction_bp.route('/user-info', methods=['GET'])
def get_user_info():
    """获取当前用户信息"""
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'is_admin': current_user.is_admin
            }
        })
    else:
        return jsonify({'success': False, 'message': '未登录'}), 401

@interaction_bp.route('/like', methods=['POST'])
@login_required
def toggle_like():
    """切换点赞状态"""
    try:
        data = request.get_json()
        content_type = data.get('type')  # 'post' or 'project'
        content_id = data.get('id')
        
        if not content_type or not content_id:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        # 获取内容对象
        if content_type == 'post':
            content = Post.query.get_or_404(content_id)
            type_code = 1  # 1-博客
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
            type_code = 2  # 2-项目
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 查找或创建用户互动记录
        interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            content_id=content_id,
            type=type_code
        ).first()
        
        if interaction:
            # 切换点赞状态
            if interaction.like == 1:
                interaction.like = 0
                content.like_count = max(0, content.like_count - 1)
                is_liked = False
            else:
                interaction.like = 1
                content.like_count += 1
                is_liked = True
            interaction.updated_at = datetime.utcnow()
        else:
            # 创建新的互动记录
            interaction = UserInteraction(
                user_id=current_user.id,
                content_id=content_id,
                type=type_code,
                like=1,
                favorite=0,
                rating=0
            )
            db.session.add(interaction)
            content.like_count += 1
            is_liked = True
        
        # 创建点赞通知（如果是点赞操作且不是自己的内容）
        if is_liked and content.author_id != current_user.id:
            create_notification_for_like(interaction, content_type, content.title, content.author_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_liked': is_liked,
            'like_count': content.like_count
        })
        
    except Exception as e:
        current_app.logger.error(f"点赞操作失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败'}), 500

@interaction_bp.route('/favorite', methods=['POST'])
@login_required
def toggle_favorite():
    """切换收藏状态"""
    try:
        data = request.get_json()
        content_type = data.get('type')  # 'post' or 'project'
        content_id = data.get('id')
        
        if not content_type or not content_id:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        # 获取内容对象
        if content_type == 'post':
            content = Post.query.get_or_404(content_id)
            type_code = 1  # 1-博客
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
            type_code = 2  # 2-项目
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 查找或创建用户互动记录
        interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            content_id=content_id,
            type=type_code
        ).first()
        
        if interaction:
            # 切换收藏状态
            if interaction.favorite == 1:
                interaction.favorite = 0
                content.favorite_count = max(0, content.favorite_count - 1)
                is_favorited = False
            else:
                interaction.favorite = 1
                content.favorite_count += 1
                is_favorited = True
            interaction.updated_at = datetime.utcnow()
        else:
            # 创建新的互动记录
            interaction = UserInteraction(
                user_id=current_user.id,
                content_id=content_id,
                type=type_code,
                like=0,
                favorite=1,
                rating=0
            )
            db.session.add(interaction)
            content.favorite_count += 1
            is_favorited = True
        
        # 创建收藏通知（如果是收藏操作且不是自己的内容）
        if is_favorited and content.author_id != current_user.id:
            create_notification_for_favorite(interaction, content_type, content.title, content.author_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_favorited': is_favorited,
            'favorite_count': content.favorite_count
        })
        
    except Exception as e:
        current_app.logger.error(f"收藏操作失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败'}), 500

@interaction_bp.route('/comment', methods=['POST'])
@login_required
def add_comment():
    """添加评论"""
    try:
        data = request.get_json()
        content_type = data.get('type')  # 'post' or 'project'
        content_id = data.get('id')
        comment_text = data.get('content', '').strip()
        
        if not content_type or not content_id or not comment_text:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        if len(comment_text) > 1000:
            return jsonify({'success': False, 'message': '评论内容过长'}), 400
        
        # 获取内容对象
        if content_type == 'post':
            content = Post.query.get_or_404(content_id)
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 创建新的评论记录（允许多条评论）
        new_comment = Comment(
            user_id=current_user.id,
            content=comment_text,
            **{f'{content_type}_id': content_id}
        )
        db.session.add(new_comment)
        
        # 重新计算评论计数（只计算有内容的评论）
        actual_comment_count = Comment.query.filter_by(
            **{f'{content_type}_id': content_id}
        ).filter(Comment.content != '').count()
        content.comment_count = actual_comment_count
        
        # 创建评论通知
        create_notification_for_comment(new_comment, content_type, content.title, content.author_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论添加成功',
            'comment_count': content.comment_count
        })
        
    except Exception as e:
        current_app.logger.error(f"添加评论失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败'}), 500

@interaction_bp.route('/comments/<int:content_id>')
def get_comments(content_id):
    """获取评论列表"""
    try:
        content_type = request.args.get('type', 'post')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if content_type == 'post':
            content = Post.query.get_or_404(content_id)
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 获取评论（只显示有内容的评论，不包括仅评分的记录）
        comments = Comment.query.filter_by(
            **{f'{content_type}_id': content_id},
            is_approved=True
        ).filter(Comment.content != '').order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        comments_data = []
        for comment in comments.items:
            i = random.randint(1, 4)
            
            # 获取评论的回复
            replies = CommentReply.query.filter_by(comment_id=comment.id, is_approved=True).order_by(CommentReply.created_at.asc()).all()
            replies_data = []
            for reply in replies:
                reply_i = random.randint(1, 4)
                replies_data.append({
                    'id': reply.id,
                    'content': reply.content,
                    'created_at': to_china_time(reply.created_at),
                    'user': {
                        'id': reply.user.id,
                        'username': reply.user.username,
                        'avatar': reply.user.avatar or f'/static/avatar/avatar{reply_i}.png'
                    }
                })
            
            # 检查当前用户是否已点赞此评论
            is_liked = False
            if current_user.is_authenticated:
                like = CommentLike.query.filter_by(
                    user_id=current_user.id,
                    comment_id=comment.id
                ).first()
                is_liked = like is not None
            
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'created_at': to_china_time(comment.created_at),
                'replies': replies_data,
                'replies_count': len(replies_data),
                'like_count': comment.like_count or 0,
                'is_liked': is_liked,
                'user': {
                    'id': comment.user.id,
                    'username': comment.user.username,
                    'avatar': comment.user.avatar or f'/static/avatar/avatar{i}.png'
                }
            })
        
        return jsonify({
            'success': True,
            'comments': comments_data,
            'pagination': {
                'page': page,
                'pages': comments.pages,
                'per_page': per_page,
                'total': comments.total,
                'has_next': comments.has_next,
                'has_prev': comments.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取评论失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取评论失败'}), 500

@interaction_bp.route('/user-status/<int:content_id>')
@login_required
def get_user_status(content_id):
    """获取用户对内容的交互状态"""
    try:
        content_type = request.args.get('type', 'post')
        
        # 确定类型代码
        if content_type == 'post':
            type_code = 1  # 1-博客
        elif content_type == 'project':
            type_code = 2  # 2-项目
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 获取用户互动记录
        interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            content_id=content_id,
            type=type_code
        ).first()
        
        if interaction:
            is_liked = interaction.like == 1
            is_favorited = interaction.favorite == 1
            user_rating = interaction.rating if interaction.rating > 0 else None
        else:
            is_liked = False
            is_favorited = False
            user_rating = None
        
        return jsonify({
            'success': True,
            'is_liked': is_liked,
            'is_favorited': is_favorited,
            'user_rating': user_rating
        })
        
    except Exception as e:
        current_app.logger.error(f"获取用户状态失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取状态失败'}), 500

@interaction_bp.route('/rating', methods=['POST'])
@login_required
def save_rating():
    """保存评分"""
    try:
        data = request.get_json()
        content_type = data.get('type')
        content_id = data.get('id')
        rating = data.get('rating')

        if not content_type or not content_id or not rating:
            return jsonify({'success': False, 'message': '参数错误: 内容、类型和评分不能为空'}), 400

        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': '评分必须在1-5之间'}), 400

        if content_type == 'post':
            content = Post.query.get_or_404(content_id)
            type_code = 1  # 1-博客
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
            type_code = 2  # 2-项目
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400

        # 查找或创建用户互动记录
        interaction = UserInteraction.query.filter_by(
            user_id=current_user.id,
            content_id=content_id,
            type=type_code
        ).first()

        if interaction:
            # 更新现有评分
            interaction.rating = rating
            interaction.updated_at = datetime.utcnow()
        else:
            # 创建新的互动记录
            interaction = UserInteraction(
                user_id=current_user.id,
                content_id=content_id,
                type=type_code,
                like=0,
                favorite=0,
                rating=rating
            )
            db.session.add(interaction)

        # 更新平均评分
        interactions_with_rating = UserInteraction.query.filter_by(
            content_id=content_id,
            type=type_code
        ).filter(UserInteraction.rating > 0).all()
        
        if interactions_with_rating:
            total_rating = sum(i.rating for i in interactions_with_rating)
            content.average_rating = round(total_rating / len(interactions_with_rating), 1)
        else:
            content.average_rating = 0.0

        # 创建评分通知（如果不是自己的内容）
        if content.author_id != current_user.id:
            create_notification_for_rating(interaction, content_type, content.title, content.author_id)

        db.session.commit()
        return jsonify({
            'success': True,
            'message': '评分保存成功',
            'average_rating': content.average_rating
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"评分保存失败: {e}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500

# 评论编辑功能已移除 - 评论不可修改

@interaction_bp.route('/comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """删除评论"""
    try:
        # 查找评论
        comment = Comment.query.get_or_404(comment_id)
        
        # 检查权限：只有评论作者或管理员可以删除
        if comment.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'message': '无权限删除此评论'}), 403

        # 获取关联的内容
        if comment.post_id:
            content_type = 'post'
            content_id = comment.post_id
            content = Post.query.get(content_id)
        elif comment.project_id:
            content_type = 'project'
            content_id = comment.project_id
            content = Project.query.get(content_id)
        else:
            return jsonify({'success': False, 'message': '评论关联的内容不存在'}), 400

        # 删除评论
        db.session.delete(comment)
        
        # 重新计算评论计数（只计算有内容的评论）
        if content:
            actual_comment_count = Comment.query.filter_by(
                **{f'{content_type}_id': content_id}
            ).filter(Comment.content != '').count()
            content.comment_count = actual_comment_count

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论删除成功',
            'comment_count': content.comment_count if content else 0
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"评论删除失败: {e}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500
@interaction_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """上传图片"""
    try:
        current_app.logger.info(f"图片上传请求 - 用户: {current_user.username}")
        current_app.logger.info(f"请求文件: {list(request.files.keys())}")
        
        if 'image' not in request.files:
            current_app.logger.warning("没有找到image字段")
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            current_app.logger.warning("文件名为空")
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        current_app.logger.info(f"文件名: {file.filename}, 内容类型: {file.content_type}")
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
        allowed_mime_types = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml'}
        
        # 检查文件扩展名
        has_valid_extension = ('.' in file.filename and 
                              file.filename.rsplit('.', 1)[1].lower() in allowed_extensions)
        
        # 检查MIME类型
        has_valid_mime = file.content_type in allowed_mime_types
        
        if not (has_valid_extension or has_valid_mime):
            return jsonify({'success': False, 'message': f'不支持的文件类型: {file.content_type}'}), 400
        
        # 检查文件大小 (5MB)
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()  # 获取文件大小
        file.seek(0)  # 重置文件指针到开头
        
        if file_size > 5 * 1024 * 1024:
            return jsonify({'success': False, 'message': '文件大小不能超过5MB'}), 400
        
        # 生成安全的文件名
        original_filename = file.filename or 'image'
        filename = secure_filename(original_filename)
        
        # 如果没有扩展名，根据MIME类型添加
        if '.' not in filename:
            mime_to_ext = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/svg+xml': '.svg'
            }
            ext = mime_to_ext.get(file.content_type, '.jpg')
            filename = f"{filename}{ext}"
        
        # 添加时间戳避免重名
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        current_app.logger.info(f"保存文件到: {file_path}")
        file.save(file_path)
        
        # 返回图片URL
        image_url = f"/static/uploads/images/{filename}"
        current_app.logger.info(f"图片上传成功: {image_url}")
        
        return jsonify({
            'success': True,
            'message': '图片上传成功',
            'url': image_url,
            'alt': name
        })
        
    except Exception as e:
        current_app.logger.error(f"图片上传失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'}), 500

@interaction_bp.route('/comments/<int:comment_id>/replies', methods=['GET'])
def get_comment_replies(comment_id):
    """获取评论的回复列表"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        replies = CommentReply.query.filter_by(comment_id=comment_id, is_approved=True).order_by(CommentReply.created_at.asc()).all()
        
        replies_data = []
        for reply in replies:
            # 获取用户头像
            avatar_url = '/static/images/default-avatar.png'
            if reply.user.avatar:
                avatar_url = f'/static/uploads/avatars/{reply.user.avatar}'
            
            replies_data.append({
                'id': reply.id,
                'content': reply.content,
                'created_at': to_china_time(reply.created_at),
                'user': {
                    'id': reply.user.id,
                    'username': reply.user.username,
                    'avatar': avatar_url
                }
            })
        
        return jsonify({
            'success': True,
            'replies': replies_data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取回复失败: {e}")
        return jsonify({'success': False, 'message': '获取回复失败'}), 500

@interaction_bp.route('/comments/<int:comment_id>/replies', methods=['POST'])
@login_required
def add_comment_reply(comment_id):
    """添加评论回复"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'message': '请输入回复内容'})
        
        reply = CommentReply(
            comment_id=comment_id,
            user_id=current_user.id,
            content=content
        )
        
        db.session.add(reply)
        
        # 创建回复通知
        # 获取评论所属的内容
        content_type = 'post' if comment.post_id else 'project'
        content_id = comment.post_id or comment.project_id
        if content_type == 'post':
            content = Post.query.get(content_id)
        else:
            content = Project.query.get(content_id)
        
        if content:
            create_notification_for_reply(reply, comment, content_type, content.title, comment.user_id)
        
        db.session.commit()
        
        # 获取用户头像
        avatar_url = '/static/images/default-avatar.png'
        if current_user.avatar:
            avatar_url = f'/static/uploads/avatars/{current_user.avatar}'
        
        return jsonify({
            'success': True,
            'message': '回复成功',
            'reply': {
                'id': reply.id,
                'content': reply.content,
                'created_at': to_china_time(reply.created_at),
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'avatar': avatar_url
                }
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加回复失败: {e}")
        return jsonify({'success': False, 'message': '添加回复失败'}), 500

# 评论回复编辑功能已移除 - 回复不可修改

@interaction_bp.route('/replies/<int:reply_id>', methods=['DELETE'])
@login_required
def delete_comment_reply(reply_id):
    """删除评论回复"""
    try:
        reply = CommentReply.query.get_or_404(reply_id)
        
        # 检查权限：只有回复作者或管理员可以删除
        if reply.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'message': '没有权限删除此回复'}), 403
        
        db.session.delete(reply)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '回复删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除回复失败: {e}")
        return jsonify({'success': False, 'message': '删除回复失败'}), 500


@interaction_bp.route('/comment-like', methods=['POST'])
@login_required
def comment_like():
    """评论点赞/取消点赞"""
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')
        
        if not comment_id:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'success': False, 'message': '评论不存在'}), 404
        
        # 检查是否已经点赞
        existing_like = CommentLike.query.filter_by(
            user_id=current_user.id,
            comment_id=comment_id
        ).first()
        
        if existing_like:
            # 取消点赞
            db.session.delete(existing_like)
            comment.like_count = max(0, comment.like_count - 1)
            liked = False
            message = '取消点赞成功'
        else:
            # 添加点赞
            like = CommentLike(
                user_id=current_user.id,
                comment_id=comment_id
            )
            db.session.add(like)
            comment.like_count += 1
            liked = True
            message = '点赞成功'
            
            # 创建点赞通知（如果不是自己的评论）
            if comment.user_id != current_user.id:
                # 获取评论所属的文章或项目
                if comment.post_id:
                    post = Post.query.get(comment.post_id)
                    if post:
                        notification = Notification.create_like_notification(
                            post.author_id, current_user.username, '文章', 
                            post.id, post.title
                        )
                        db.session.add(notification)
                elif comment.project_id:
                    project = Project.query.get(comment.project_id)
                    if project:
                        notification = Notification.create_like_notification(
                            project.author_id, current_user.username, '项目', 
                            project.id, project.title
                        )
                        db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'liked': liked,
            'like_count': comment.like_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"评论点赞失败: {e}")
        return jsonify({'success': False, 'message': '操作失败'}), 500


def create_notification_for_comment(comment, content_type, content_title, content_author_id):
    """为评论创建通知"""
    try:
        # 如果不是自己的内容，创建通知
        if content_author_id != comment.user_id:
            notification = Notification.create_comment_notification(
                content_author_id, comment.user.username, comment.content,
                comment.post_id or comment.project_id, content_title
            )
            db.session.add(notification)
    except Exception as e:
        current_app.logger.error(f"创建评论通知失败: {e}")


def create_notification_for_reply(reply, comment, content_type, content_title, comment_author_id):
    """为回复创建通知"""
    try:
        # 如果不是回复自己的评论，创建通知
        if comment_author_id != reply.user_id:
            notification = Notification.create_reply_notification(
                comment_author_id, reply.user.username, reply.content,
                comment.id, comment.post_id or comment.project_id, content_title
            )
            db.session.add(notification)
    except Exception as e:
        current_app.logger.error(f"创建回复通知失败: {e}")


def create_notification_for_like(interaction, content_type, content_title, content_author_id):
    """为点赞创建通知"""
    try:
        # 如果不是自己的内容，创建通知
        if content_author_id != interaction.user_id:
            notification = Notification.create_like_notification(
                content_author_id, interaction.user.username, content_type,
                interaction.content_id, content_title
            )
            db.session.add(notification)
    except Exception as e:
        current_app.logger.error(f"创建点赞通知失败: {e}")


def create_notification_for_favorite(interaction, content_type, content_title, content_author_id):
    """为收藏创建通知"""
    try:
        # 如果不是自己的内容，创建通知
        if content_author_id != interaction.user_id:
            notification = Notification.create_favorite_notification(
                content_author_id, interaction.user.username, content_type,
                interaction.content_id, content_title
            )
            db.session.add(notification)
    except Exception as e:
        current_app.logger.error(f"创建收藏通知失败: {e}")


def create_notification_for_rating(interaction, content_type, content_title, content_author_id):
    """为评分创建通知"""
    try:
        # 如果不是自己的内容，创建通知
        if content_author_id != interaction.user_id:
            notification = Notification.create_rating_notification(
                content_author_id, interaction.user.username, interaction.rating,
                content_type, interaction.content_id, content_title
            )
            db.session.add(notification)
    except Exception as e:
        current_app.logger.error(f"创建评分通知失败: {e}")
