import random

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import db
from app.models import Post, Project, Comment, CommentReply, UserInteraction
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
            
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'created_at': to_china_time(comment.created_at),
                'replies': replies_data,
                'replies_count': len(replies_data),
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
        # 检查是否有文件
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        file = request.files['image']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': '不支持的文件类型'}), 400
        
        # 检查文件大小 (5MB限制)
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'success': False, 'message': '文件大小不能超过5MB'}), 400
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加UUID前缀避免文件名冲突
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 返回图片URL
        image_url = f"/static/uploads/images/{unique_filename}"
        
        return jsonify({
            'success': True,
            'message': '图片上传成功',
            'image_url': image_url
        })
        
    except Exception as e:
        current_app.logger.error(f"图片上传失败: {e}")
        return jsonify({'success': False, 'message': '图片上传失败'}), 500

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
