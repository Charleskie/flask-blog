from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import db
from app.models import Post, Project, Like, Favorite, Comment
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

interaction_bp = Blueprint('interaction', __name__)

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
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 检查是否已经点赞
        existing_like = Like.query.filter_by(
            user_id=current_user.id,
            **{f'{content_type}_id': content_id}
        ).first()
        
        if existing_like:
            # 取消点赞
            db.session.delete(existing_like)
            content.like_count = max(0, content.like_count - 1)
            is_liked = False
        else:
            # 添加点赞
            new_like = Like(
                user_id=current_user.id,
                **{f'{content_type}_id': content_id}
            )
            db.session.add(new_like)
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
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400
        
        # 检查是否已经收藏
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            **{f'{content_type}_id': content_id}
        ).first()
        
        if existing_favorite:
            # 取消收藏
            db.session.delete(existing_favorite)
            content.favorite_count = max(0, content.favorite_count - 1)
            is_favorited = False
        else:
            # 添加收藏
            new_favorite = Favorite(
                user_id=current_user.id,
                **{f'{content_type}_id': content_id}
            )
            db.session.add(new_favorite)
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
        
        # 查找用户是否已有评论记录
        existing_comment = Comment.query.filter_by(
            user_id=current_user.id,
            **{f'{content_type}_id': content_id}
        ).first()

        if existing_comment:
            # 更新现有评论的内容
            if not existing_comment.content:  # 如果之前只有评分没有内容
                content.comment_count += 1
            existing_comment.content = comment_text
        else:
            # 创建新的评论记录
            new_comment = Comment(
                user_id=current_user.id,
                content=comment_text,
                rating=None,
                **{f'{content_type}_id': content_id}
            )
            db.session.add(new_comment)
            content.comment_count += 1
        
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
        
        # 获取评论
        comments = Comment.query.filter_by(
            **{f'{content_type}_id': content_id},
            is_approved=True
        ).order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        comments_data = []
        for comment in comments.items:
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'rating': comment.rating,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'user': {
                    'id': comment.user.id,
                    'username': comment.user.username,
                    'avatar': comment.user.avatar or '/static/images/default-avatar.png'
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
        
        # 检查点赞状态
        is_liked = Like.query.filter_by(
            user_id=current_user.id,
            **{f'{content_type}_id': content_id}
        ).first() is not None
        
        # 检查收藏状态
        is_favorited = Favorite.query.filter_by(
            user_id=current_user.id,
            **{f'{content_type}_id': content_id}
        ).first() is not None
        
        return jsonify({
            'success': True,
            'is_liked': is_liked,
            'is_favorited': is_favorited
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

        if content_type == 'post':
            content = Post.query.get_or_404(content_id)
        elif content_type == 'project':
            content = Project.query.get_or_404(content_id)
        else:
            return jsonify({'success': False, 'message': '类型错误'}), 400

        # 查找用户是否已有评论记录
        existing_comment = Comment.query.filter_by(
            user_id=current_user.id,
            **{f'{content_type}_id': content_id}
        ).first()

        if existing_comment:
            # 更新现有评论的评分
            existing_comment.rating = rating
        else:
            # 创建新的评论记录（仅评分，无内容）
            new_comment = Comment(
                user_id=current_user.id,
                content='',  # 空内容，仅评分
                rating=rating,
                **{f'{content_type}_id': content_id}
            )
            db.session.add(new_comment)

        # 更新平均评分
        comments_with_rating = Comment.query.filter_by(
            **{f'{content_type}_id': content_id}
        ).filter(Comment.rating.isnot(None)).all()
        
        if comments_with_rating:
            total_rating = sum(c.rating for c in comments_with_rating)
            content.average_rating = round(total_rating / len(comments_with_rating), 1)
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

@interaction_bp.route('/comment/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(comment_id):
    """更新评论"""
    try:
        data = request.get_json()
        new_content = data.get('content', '').strip()
        new_rating = data.get('rating')

        current_app.logger.info(f"更新评论请求 - comment_id: {comment_id}, content: {new_content}, rating: {new_rating}")

        if not new_content:
            return jsonify({'success': False, 'message': '评论内容不能为空'}), 400

        if len(new_content) > 1000:
            return jsonify({'success': False, 'message': '评论内容过长'}), 400

        # 查找评论
        comment = Comment.query.get_or_404(comment_id)
        current_app.logger.info(f"找到评论 - id: {comment.id}, 原内容: {comment.content}, 原评分: {comment.rating}")
        
        # 检查权限：只有评论作者或管理员可以修改
        if comment.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'message': '无权限修改此评论'}), 403

        # 更新评论内容
        comment.content = new_content
        
        # 更新评分（如果提供）
        if new_rating is not None:
            current_app.logger.info(f"更新评分 - 从 {comment.rating} 到 {new_rating}")
            comment.rating = new_rating
        else:
            current_app.logger.info(f"未提供评分，保持原评分: {comment.rating}")
        # 注意：如果new_rating为None，我们不更新评分字段，保持原有评分

        # 更新平均评分
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

        current_app.logger.info(f"关联内容 - type: {content_type}, id: {content_id}")

        if content:
            comments_with_rating = Comment.query.filter_by(
                **{f'{content_type}_id': content_id}
            ).filter(Comment.rating.isnot(None)).all()
            
            current_app.logger.info(f"有评分的评论数量: {len(comments_with_rating)}")
            for c in comments_with_rating:
                current_app.logger.info(f"评论 {c.id}: 评分 {c.rating}")
            
            if comments_with_rating:
                total_rating = sum(c.rating for c in comments_with_rating)
                new_average = round(total_rating / len(comments_with_rating), 1)
                current_app.logger.info(f"计算平均评分: {total_rating} / {len(comments_with_rating)} = {new_average}")
                content.average_rating = new_average
            else:
                current_app.logger.info("没有评分，设置平均评分为0")
                content.average_rating = 0.0

        db.session.commit()
        current_app.logger.info(f"评论更新成功 - 新内容: {comment.content}, 新评分: {comment.rating}")
        
        return jsonify({
            'success': True,
            'message': '评论更新成功',
            'average_rating': content.average_rating if content else 0.0
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"评论更新失败: {e}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500

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
        
        # 更新评论计数
        if content:
            content.comment_count = max(0, content.comment_count - 1)
            
            # 重新计算平均评分
            comments_with_rating = Comment.query.filter_by(
                **{f'{content_type}_id': content_id}
            ).filter(Comment.rating.isnot(None)).all()
            
            if comments_with_rating:
                total_rating = sum(c.rating for c in comments_with_rating)
                content.average_rating = round(total_rating / len(comments_with_rating), 1)
            else:
                content.average_rating = 0.0

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '评论删除成功',
            'comment_count': content.comment_count if content else 0,
            'average_rating': content.average_rating if content else 0.0
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
