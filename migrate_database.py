#!/usr/bin/env python3
"""
数据库迁移脚本
用于更新Post表结构，添加新字段
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Post, User

def migrate_database():
    """执行数据库迁移"""
    print("🔄 开始数据库迁移...")
    
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
            
            # 更新现有文章
            posts = Post.query.all()
            if posts:
                print(f"📝 更新 {len(posts)} 篇现有文章...")
                
                for post in posts:
                    # 设置默认状态为已发布
                    if not hasattr(post, 'status') or not post.status:
                        post.status = 'published'
                    
                    # 生成slug
                    if not hasattr(post, 'slug') or not post.slug:
                        post.slug = post.generate_slug()
                    
                    # 设置默认浏览次数
                    if not hasattr(post, 'view_count'):
                        post.view_count = 0
                
                db.session.commit()
                print("✅ 现有文章更新完成")
            
            # 创建示例文章（如果没有文章）
            if not posts:
                print("📝 创建示例文章...")
                
                # 确保有用户
                user = User.query.first()
                if not user:
                    print("⚠️  没有找到用户，请先注册一个用户")
                    return
                
                # 创建示例文章
                sample_posts = [
                    {
                        'title': '欢迎来到我的个人网站',
                        'content': '''# 欢迎来到我的个人网站

这是我的第一篇博客文章，用来测试文章功能。

## 功能特性

- ✅ 文章发布和管理
- ✅ 分类和标签
- ✅ 富文本编辑
- ✅ 文章预览

## 技术栈

- **后端**: Flask + SQLAlchemy
- **前端**: Bootstrap 5 + Font Awesome
- **数据库**: SQLite

希望这个网站能为大家提供有价值的内容！''',
                        'excerpt': '欢迎来到我的个人网站，这里将分享技术文章、项目经验和生活感悟。',
                        'category': '随笔',
                        'tags': '欢迎,介绍,技术',
                        'status': 'published'
                    },
                    {
                        'title': 'Flask Web开发入门指南',
                        'content': '''# Flask Web开发入门指南

Flask是一个轻量级的Python Web框架，非常适合初学者学习Web开发。

## 为什么选择Flask？

1. **简单易学**: 核心概念简单，学习曲线平缓
2. **灵活性高**: 可以根据需要选择组件
3. **文档完善**: 官方文档详细，社区活跃
4. **扩展丰富**: 大量第三方扩展可用

## 快速开始

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```

## 下一步

- 学习路由和视图函数
- 了解模板系统
- 掌握数据库集成
- 部署到生产环境

继续关注更多Flask教程！''',
                        'excerpt': 'Flask是一个轻量级的Python Web框架，本文介绍Flask的基础知识和快速入门方法。',
                        'category': '教程',
                        'tags': 'Flask,Python,Web开发,教程',
                        'status': 'published'
                    }
                ]
                
                for post_data in sample_posts:
                    post = Post(
                        title=post_data['title'],
                        content=post_data['content'],
                        excerpt=post_data['excerpt'],
                        category=post_data['category'],
                        tags=post_data['tags'],
                        status=post_data['status'],
                        author_id=user.id
                    )
                    post.slug = post.generate_slug()
                    db.session.add(post)
                
                db.session.commit()
                print("✅ 示例文章创建完成")
            
            print("🎉 数据库迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_database() 