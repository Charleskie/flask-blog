from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Version
from app.models.user import db
from app.utils import admin_required
from datetime import datetime

version_bp = Blueprint('version', __name__)

@version_bp.route('/admin/versions')
@login_required
@admin_required
def admin_versions():
    """版本管理页面"""
    versions = Version.query.order_by(Version.release_date.desc()).all()
    return render_template('admin/admin_versions.html', versions=versions)

@version_bp.route('/admin/versions/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_version():
    """创建新版本"""
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX请求，返回JSON
            try:
                version_number = request.json.get('version_number', '').strip()
                title = request.json.get('title', '').strip()
                description = request.json.get('description', '').strip()
                release_date_str = request.json.get('release_date', '')
                
                if not version_number or not title or not description:
                    return jsonify({'success': False, 'message': '请填写所有必填字段'})
                
                # 检查版本号是否已存在
                existing_version = Version.query.filter_by(version_number=version_number).first()
                if existing_version:
                    return jsonify({'success': False, 'message': '版本号已存在'})
                
                # 解析发布日期
                release_date = datetime.utcnow()
                if release_date_str:
                    try:
                        release_date = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                
                version = Version(
                    version_number=version_number,
                    title=title,
                    description=description,
                    release_date=release_date
                )
                
                db.session.add(version)
                db.session.commit()
                
                return jsonify({'success': True, 'message': '版本创建成功！'})
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': '创建失败，请稍后重试'})
        else:
            # 传统表单提交
            version_number = request.form.get('version_number', '').strip()
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            release_date_str = request.form.get('release_date', '')
            
            if not version_number or not title or not description:
                return render_template('admin/new_version.html', error='请填写所有必填字段')
            
            # 检查版本号是否已存在
            existing_version = Version.query.filter_by(version_number=version_number).first()
            if existing_version:
                return render_template('admin/new_version.html', error='版本号已存在')
            
            # 解析发布日期
            release_date = datetime.utcnow()
            if release_date_str:
                try:
                    release_date = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            version = Version(
                version_number=version_number,
                title=title,
                description=description,
                release_date=release_date
            )
            
            db.session.add(version)
            db.session.commit()
            
            return redirect(url_for('version.admin_versions'))
    
    return render_template('admin/new_version.html')

@version_bp.route('/admin/versions/<int:version_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_version(version_id):
    """编辑版本"""
    version = Version.query.get_or_404(version_id)
    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX请求，返回JSON
            try:
                version_number = request.json.get('version_number', '').strip()
                title = request.json.get('title', '').strip()
                description = request.json.get('description', '').strip()
                release_date_str = request.json.get('release_date', '')
                
                if not version_number or not title or not description:
                    return jsonify({'success': False, 'message': '请填写所有必填字段'})
                
                # 检查版本号是否已被其他版本使用
                existing_version = Version.query.filter(
                    Version.version_number == version_number,
                    Version.id != version_id
                ).first()
                if existing_version:
                    return jsonify({'success': False, 'message': '版本号已存在'})
                
                # 解析发布日期
                if release_date_str:
                    try:
                        release_date = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
                        version.release_date = release_date
                    except ValueError:
                        pass
                
                version.version_number = version_number
                version.title = title
                version.description = description
                version.updated_at = datetime.utcnow()
                
                db.session.commit()
                
                return jsonify({'success': True, 'message': '版本更新成功！'})
                
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': '更新失败，请稍后重试'})
        else:
            # 传统表单提交
            version_number = request.form.get('version_number', '').strip()
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            release_date_str = request.form.get('release_date', '')
            
            if not version_number or not title or not description:
                return render_template('admin/edit_version.html', version=version, error='请填写所有必填字段')
            
            # 检查版本号是否已被其他版本使用
            existing_version = Version.query.filter(
                Version.version_number == version_number,
                Version.id != version_id
            ).first()
            if existing_version:
                return render_template('admin/edit_version.html', version=version, error='版本号已存在')
            
            # 解析发布日期
            if release_date_str:
                try:
                    release_date = datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
                    version.release_date = release_date
                except ValueError:
                    pass
            
            version.version_number = version_number
            version.title = title
            version.description = description
            version.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return redirect(url_for('version.admin_versions'))
    
    return render_template('admin/edit_version.html', version=version)

@version_bp.route('/admin/versions/<int:version_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_version(version_id):
    """删除版本"""
    version = Version.query.get_or_404(version_id)
    
    try:
        db.session.delete(version)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '版本删除成功！'})
        else:
            return redirect(url_for('version.admin_versions'))
            
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
        else:
            return redirect(url_for('version.admin_versions'))

@version_bp.route('/api/versions')
def get_versions():
    """获取版本列表API（用于首页展示）"""
    versions = Version.query.filter_by(is_active=True).order_by(Version.release_date.desc()).all()
    return jsonify({
        'success': True,
        'versions': [version.to_dict() for version in versions]
    })
