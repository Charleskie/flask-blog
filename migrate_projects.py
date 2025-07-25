#!/usr/bin/env python3
"""
项目数据库迁移脚本
用于更新Project表结构，添加新字段
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Project, User

def migrate_projects():
    """执行项目数据库迁移"""
    print("🔄 开始项目数据库迁移...")
    
    with app.app_context():
        try:
            # 检查是否需要创建新表
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # 强制删除并重新创建所有表
            print("🗑️  删除现有表...")
            db.drop_all()
            print("📝 重新创建所有表...")
            db.create_all()
            print("✅ 表结构创建成功")
            
            # 更新现有项目
            projects = Project.query.all()
            if projects:
                print(f"📝 更新 {len(projects)} 个现有项目...")
                
                for project in projects:
                    # 设置默认状态为活跃
                    if not hasattr(project, 'status') or not project.status:
                        project.status = 'active'
                    
                    # 设置默认浏览次数
                    if not hasattr(project, 'view_count'):
                        project.view_count = 0
                    
                    # 设置默认推荐状态
                    if not hasattr(project, 'featured'):
                        project.featured = False
                
                db.session.commit()
                print("✅ 现有项目更新完成")
            
            # 创建示例项目（如果没有项目）
            if not projects:
                print("📝 创建示例项目...")
                
                # 确保有用户
                user = User.query.first()
                if not user:
                    print("⚠️  没有找到用户，请先注册一个用户")
                    return
                
                # 创建示例项目
                sample_projects = [
                    {
                        'title': '个人网站系统',
                        'short_description': '基于Flask开发的现代化个人网站，包含博客、项目管理等功能',
                        'description': '''这是一个使用Flask框架开发的个人网站系统，具有以下特点：

## 主要功能
- 用户认证系统（注册、登录、密码重置）
- 博客文章管理（发布、编辑、分类、标签）
- 项目展示管理（项目信息、技术栈、链接）
- 响应式设计，支持移动端访问
- 管理后台，方便内容管理

## 技术栈
- 后端：Flask + SQLAlchemy + Flask-Login
- 前端：Bootstrap 5 + Font Awesome + JavaScript
- 数据库：SQLite
- 部署：支持Docker、Heroku、Vercel等

## 项目亮点
- 完整的用户认证系统
- 现代化的UI设计
- 响应式布局
- 易于扩展的架构
- 详细的文档说明''',
                        'category': 'Web应用',
                        'tags': 'Flask,Python,Web开发,个人网站',
                        'technologies': 'Flask, SQLAlchemy, Bootstrap 5, SQLite, Python',
                        'features': '用户认证\n博客管理\n项目管理\n响应式设计\n管理后台',
                        'challenges': '在开发过程中，最大的挑战是设计一个既美观又实用的用户界面，同时确保系统的安全性和可扩展性。',
                        'lessons_learned': '通过这个项目，我深入学习了Flask框架的使用，掌握了Web开发的最佳实践，也学会了如何设计用户友好的界面。',
                        'status': 'completed',
                        'featured': True,
                        'github_url': 'https://github.com/username/personal-website',
                        'live_url': 'https://personal-website-demo.com',
                        'image_url': 'https://via.placeholder.com/400x300/007bff/ffffff?text=个人网站'
                    },
                    {
                        'title': '数据分析工具',
                        'short_description': 'Python数据分析工具，支持多种数据格式处理和可视化',
                        'description': '''这是一个功能强大的数据分析工具，支持多种数据格式的导入、处理和分析。

## 主要功能
- 支持CSV、Excel、JSON等多种数据格式
- 数据清洗和预处理
- 统计分析功能
- 数据可视化（图表生成）
- 报告导出功能

## 技术栈
- Python + Pandas + NumPy
- Matplotlib + Seaborn
- Streamlit（Web界面）
- SQLite（数据存储）

## 项目亮点
- 用户友好的Web界面
- 强大的数据处理能力
- 丰富的可视化选项
- 支持批量处理''',
                        'category': '数据分析',
                        'tags': 'Python,数据分析,Pandas,可视化',
                        'technologies': 'Python, Pandas, NumPy, Matplotlib, Streamlit',
                        'features': '多格式数据导入\n数据清洗\n统计分析\n可视化图表\n报告导出',
                        'challenges': '处理大量数据时的性能优化是一个挑战，需要合理使用数据结构和算法。',
                        'lessons_learned': '学会了如何设计高效的数据处理流程，以及如何创建用户友好的数据分析工具。',
                        'status': 'active',
                        'featured': False,
                        'github_url': 'https://github.com/username/data-analysis-tool',
                        'demo_url': 'https://data-tool-demo.streamlit.app'
                    }
                ]
                
                for project_data in sample_projects:
                    project = Project(
                        title=project_data['title'],
                        short_description=project_data['short_description'],
                        description=project_data['description'],
                        category=project_data['category'],
                        tags=project_data['tags'],
                        technologies=project_data['technologies'],
                        features=project_data['features'],
                        challenges=project_data['challenges'],
                        lessons_learned=project_data['lessons_learned'],
                        status=project_data['status'],
                        featured=project_data['featured'],
                        github_url=project_data.get('github_url'),
                        live_url=project_data.get('live_url'),
                        demo_url=project_data.get('demo_url'),
                        image_url=project_data.get('image_url')
                    )
                    db.session.add(project)
                
                db.session.commit()
                print("✅ 示例项目创建完成")
            
            print("🎉 项目数据库迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_projects() 