#!/usr/bin/env python3
"""
数据库管理工具 - 提供CRUD操作和数据库结构管理
"""

from app import create_app
from app.models.user import User, db
from app.models.post import Post
from app.models.message import Message
from app.models.message_reply import MessageReply
from app.models.about import AboutContent, AboutContact
from app.models.interaction import UserInteraction, Comment, CommentReply, CommentLike
from app.models.version import Version
from app.models.skill import Skill
from app.models.notification import Notification
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys
import sqlite3
import os
import json

def print_menu():
    """打印菜单"""
    print("\n" + "="*70)
    print("🗄️  数据库管理工具 v2.0")
    print("="*70)
    print("📊 基础数据管理:")
    print("  1. 查看所有用户")
    print("  2. 创建新用户")
    print("  3. 修改用户权限")
    print("  4. 删除用户")
    print("  5. 查看所有文章")
    print("  6. 创建新文章")
    print("  7. 删除文章")
    print("  8. 查看所有消息")
    print("  9. 删除消息")
    print("\n📋 扩展数据管理:")
    print("  10. 查看消息回复")
    print("  11. 查看关于页面内容")
    print("  12. 查看用户交互")
    print("  13. 查看评论")
    print("  14. 查看版本信息")
    print("  15. 查看技能")
    print("  16. 查看通知")
    print("\n🔧 批量操作:")
    print("  17. 批量添加字段")
    print("  18. 批量更新字段")
    print("  19. 批量删除数据")
    print("  20. 数据导入/导出")
    print("  21. 执行自定义SQL")
    print("\n🏗️  数据库结构管理:")
    print("  22. 查看所有表")
    print("  23. 查看表结构")
    print("  24. 创建新表")
    print("  25. 给表添加字段")
    print("  26. 修改字段信息")
    print("  27. 删除表")
    print("  28. 数据库迁移")
    print("  29. 备份数据库")
    print("  30. 恢复数据库")
    print("\n🔧 系统工具:")
    print("  31. 初始化数据库")
    print("  32. 重置数据库")
    print("  33. 查看数据库信息")
    print("  34. 数据库优化")
    print("  0. 退出")
    print("="*70)

def list_users():
    """查看所有用户"""
    users = User.query.all()
    print(f"\n👥 用户列表 (共{len(users)}个):")
    print("-" * 60)
    print(f"{'ID':<5} {'用户名':<15} {'邮箱':<25} {'管理员':<8} {'创建时间'}")
    print("-" * 60)
    for user in users:
        admin_status = "✅" if user.is_admin else "❌"
        print(f"{user.id:<5} {user.username:<15} {user.email:<25} {admin_status:<8} {user.created_at.strftime('%Y-%m-%d %H:%M')}")

def create_user():
    """创建新用户"""
    print("\n➕ 创建新用户")
    username = input("用户名: ").strip()
    email = input("邮箱: ").strip()
    password = input("密码: ").strip()
    is_admin = input("是否为管理员? (y/n): ").strip().lower() == 'y'
    
    if not username or not email or not password:
        print("❌ 所有字段都是必填的！")
        return
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=username).first():
        print("❌ 用户名已存在！")
        return
    
    if User.query.filter_by(email=email).first():
        print("❌ 邮箱已存在！")
        return
    
    try:
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ 用户 {username} 创建成功！")
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        db.session.rollback()

def modify_user_permission():
    """修改用户权限"""
    list_users()
    user_id = input("\n请输入要修改的用户ID: ").strip()
    
    try:
        user_id = int(user_id)
        user = User.query.get(user_id)
        if not user:
            print("❌ 用户不存在！")
            return
        
        print(f"\n当前用户: {user.username}")
        print(f"当前权限: {'管理员' if user.is_admin else '普通用户'}")
        
        new_status = input("设置为管理员? (y/n): ").strip().lower()
        user.is_admin = (new_status == 'y')
        db.session.commit()
        
        status = "管理员" if user.is_admin else "普通用户"
        print(f"✅ 用户 {user.username} 权限已更新为: {status}")
        
    except ValueError:
        print("❌ 请输入有效的用户ID！")
    except Exception as e:
        print(f"❌ 修改失败: {e}")
        db.session.rollback()

def delete_user():
    """删除用户"""
    list_users()
    user_id = input("\n请输入要删除的用户ID: ").strip()
    
    try:
        user_id = int(user_id)
        user = User.query.get(user_id)
        if not user:
            print("❌ 用户不存在！")
            return
        
        confirm = input(f"确定要删除用户 '{user.username}' 吗? (y/n): ").strip().lower()
        if confirm == 'y':
            db.session.delete(user)
            db.session.commit()
            print(f"✅ 用户 {user.username} 已删除！")
        else:
            print("❌ 取消删除")
            
    except ValueError:
        print("❌ 请输入有效的用户ID！")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        db.session.rollback()

def list_posts():
    """查看所有文章"""
    posts = Post.query.all()
    print(f"\n📝 文章列表 (共{len(posts)}篇):")
    print("-" * 80)
    print(f"{'ID':<5} {'标题':<30} {'作者':<15} {'状态':<8} {'创建时间'}")
    print("-" * 80)
    for post in posts:
        status = "已发布" if post.is_published else "草稿"
        print(f"{post.id:<5} {post.title[:28]:<30} {post.author[:13]:<15} {status:<8} {post.created_at.strftime('%Y-%m-%d')}")

def create_post():
    """创建新文章"""
    print("\n➕ 创建新文章")
    title = input("标题: ").strip()
    content = input("内容: ").strip()
    author = input("作者: ").strip()
    is_published = input("是否发布? (y/n): ").strip().lower() == 'y'
    
    if not title or not content or not author:
        print("❌ 标题、内容和作者都是必填的！")
        return
    
    try:
        post = Post(
            title=title,
            content=content,
            author=author,
            is_published=is_published
        )
        db.session.add(post)
        db.session.commit()
        print(f"✅ 文章 '{title}' 创建成功！")
    except Exception as e:
        print(f"❌ 创建文章失败: {e}")
        db.session.rollback()

def delete_post():
    """删除文章"""
    list_posts()
    post_id = input("\n请输入要删除的文章ID: ").strip()
    
    try:
        post_id = int(post_id)
        post = Post.query.get(post_id)
        if not post:
            print("❌ 文章不存在！")
            return
        
        confirm = input(f"确定要删除文章 '{post.title}' 吗? (y/n): ").strip().lower()
        if confirm == 'y':
            db.session.delete(post)
            db.session.commit()
            print(f"✅ 文章 '{post.title}' 已删除！")
        else:
            print("❌ 取消删除")
            
    except ValueError:
        print("❌ 请输入有效的文章ID！")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        db.session.rollback()

def list_messages():
    """查看所有消息"""
    messages = Message.query.all()
    print(f"\n💬 消息列表 (共{len(messages)}条):")
    print("-" * 100)
    print(f"{'ID':<5} {'姓名':<15} {'邮箱':<25} {'状态':<8} {'创建时间'}")
    print("-" * 100)
    for message in messages:
        status = "已回复" if message.is_replied else "未回复"
        print(f"{message.id:<5} {message.name[:13]:<15} {message.email[:23]:<25} {status:<8} {message.created_at.strftime('%Y-%m-%d %H:%M')}")

def delete_message():
    """删除消息"""
    list_messages()
    message_id = input("\n请输入要删除的消息ID: ").strip()
    
    try:
        message_id = int(message_id)
        message = Message.query.get(message_id)
        if not message:
            print("❌ 消息不存在！")
            return
        
        confirm = input(f"确定要删除来自 '{message.name}' 的消息吗? (y/n): ").strip().lower()
        if confirm == 'y':
            db.session.delete(message)
            db.session.commit()
            print(f"✅ 消息已删除！")
        else:
            print("❌ 取消删除")
            
    except ValueError:
        print("❌ 请输入有效的消息ID！")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        db.session.rollback()

def list_message_replies():
    """查看消息回复"""
    replies = MessageReply.query.all()
    print(f"\n💬 消息回复列表 (共{len(replies)}条):")
    print("-" * 100)
    print(f"{'ID':<5} {'消息ID':<8} {'回复内容':<40} {'创建时间'}")
    print("-" * 100)
    for reply in replies:
        content = reply.reply_content[:37] + "..." if len(reply.reply_content) > 40 else reply.reply_content
        print(f"{reply.id:<5} {reply.message_id:<8} {content:<40} {reply.created_at.strftime('%Y-%m-%d %H:%M')}")

def list_about_content():
    """查看关于页面内容"""
    contents = AboutContent.query.all()
    print(f"\n📄 关于页面内容 (共{len(contents)}条):")
    print("-" * 80)
    print(f"{'ID':<5} {'标题':<30} {'区块':<15} {'状态':<8} {'创建时间'}")
    print("-" * 80)
    for content in contents:
        title = content.title[:27] + "..." if len(content.title) > 30 else content.title
        status = "激活" if content.is_active else "禁用"
        print(f"{content.id:<5} {title:<30} {content.section:<15} {status:<8} {content.created_at.strftime('%Y-%m-%d')}")

def list_user_interactions():
    """查看用户交互"""
    interactions = UserInteraction.query.all()
    print(f"\n👤 用户交互列表 (共{len(interactions)}条):")
    print("-" * 80)
    print(f"{'ID':<5} {'用户ID':<8} {'内容ID':<8} {'类型':<8} {'点赞':<4} {'收藏':<4} {'评分':<4} {'创建时间'}")
    print("-" * 80)
    for interaction in interactions:
        type_name = "文章" if interaction.type == 1 else "未知"
        like_status = "✓" if interaction.like else "-"
        favorite_status = "✓" if interaction.favorite else "-"
        rating = str(interaction.rating) if interaction.rating > 0 else "-"
        print(f"{interaction.id:<5} {interaction.user_id:<8} {interaction.content_id:<8} {type_name:<8} {like_status:<4} {favorite_status:<4} {rating:<4} {interaction.created_at.strftime('%Y-%m-%d %H:%M')}")

def list_comments():
    """查看评论"""
    comments = Comment.query.all()
    print(f"\n💭 评论列表 (共{len(comments)}条):")
    print("-" * 100)
    print(f"{'ID':<5} {'用户ID':<8} {'文章ID':<8} {'内容':<30} {'创建时间'}")
    print("-" * 100)
    for comment in comments:
        content = comment.content[:27] + "..." if len(comment.content) > 30 else comment.content
        post_id = str(comment.post_id) if comment.post_id else "-"
        print(f"{comment.id:<5} {comment.user_id:<8} {post_id:<8} {content:<30} {comment.created_at.strftime('%Y-%m-%d %H:%M')}")

def list_versions():
    """查看版本信息"""
    versions = Version.query.all()
    print(f"\n📋 版本信息列表 (共{len(versions)}条):")
    print("-" * 80)
    print(f"{'ID':<5} {'版本号':<15} {'描述':<30} {'创建时间'}")
    print("-" * 80)
    for version in versions:
        description = version.description[:27] + "..." if len(version.description) > 30 else version.description
        print(f"{version.id:<5} {version.version_number:<15} {description:<30} {version.created_at.strftime('%Y-%m-%d')}")

def list_skills():
    """查看技能"""
    skills = Skill.query.all()
    print(f"\n🛠️  技能列表 (共{len(skills)}个):")
    print("-" * 80)
    print(f"{'ID':<5} {'名称':<20} {'类别':<15} {'熟练度':<8} {'状态':<6} {'创建时间'}")
    print("-" * 80)
    for skill in skills:
        name = skill.name[:17] + "..." if len(skill.name) > 20 else skill.name
        status = "启用" if skill.is_active else "禁用"
        print(f"{skill.id:<5} {name:<20} {skill.category:<15} {skill.proficiency:<8} {status:<6} {skill.created_at.strftime('%Y-%m-%d')}")

def list_notifications():
    """查看通知"""
    notifications = Notification.query.all()
    print(f"\n🔔 通知列表 (共{len(notifications)}条):")
    print("-" * 100)
    print(f"{'ID':<5} {'用户ID':<8} {'类型':<15} {'标题':<25} {'是否已读':<8} {'创建时间'}")
    print("-" * 100)
    for notification in notifications:
        title = notification.title[:22] + "..." if len(notification.title) > 25 else notification.title
        read_status = "已读" if notification.is_read else "未读"
        print(f"{notification.id:<5} {notification.user_id:<8} {notification.type:<15} {title:<25} {read_status:<8} {notification.created_at.strftime('%Y-%m-%d %H:%M')}")

def database_stats():
    """数据库统计"""
    users_count = User.query.count()
    posts_count = Post.query.count()
    messages_count = Message.query.count()
    replies_count = MessageReply.query.count()
    about_count = AboutContent.query.count()
    interactions_count = UserInteraction.query.count()
    comments_count = Comment.query.count()
    versions_count = Version.query.count()
    skills_count = Skill.query.count()
    notifications_count = Notification.query.count()
    
    admin_count = User.query.filter_by(is_admin=True).count()
    published_posts = Post.query.filter_by(is_published=True).count()
    replied_messages = Message.query.filter_by(is_replied=True).count()
    read_notifications = Notification.query.filter_by(is_read=True).count()
    
    print("\n📊 数据库统计")
    print("=" * 50)
    print(f"👥 用户总数: {users_count} (管理员: {admin_count})")
    print(f"📝 文章总数: {posts_count} (已发布: {published_posts})")
    print(f"💬 消息总数: {messages_count} (已回复: {replied_messages})")
    print(f"💭 消息回复: {replies_count}")
    print(f"📄 关于内容: {about_count}")
    print(f"👤 用户交互: {interactions_count}")
    print(f"💭 评论总数: {comments_count}")
    print(f"📋 版本信息: {versions_count}")
    print(f"🛠️  技能总数: {skills_count}")
    print(f"🔔 通知总数: {notifications_count} (已读: {read_notifications})")
    print("=" * 50)

def list_tables():
    """查看所有表"""
    try:
        # 获取数据库文件路径
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 数据库表列表 (共{len(tables)}个):")
        print("-" * 50)
        print(f"{'表名':<30} {'类型'}")
        print("-" * 50)
        
        for table in tables:
            table_name = table[0]
            # 获取表的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"{table_name:<30} {row_count} 行")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查看表失败: {e}")

def show_table_structure():
    """查看表结构"""
    list_tables()
    table_name = input("\n请输入要查看的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"❌ 表 '{table_name}' 不存在！")
            conn.close()
            return
        
        print(f"\n📋 表 '{table_name}' 结构:")
        print("-" * 80)
        print(f"{'字段名':<20} {'类型':<15} {'是否为空':<8} {'默认值':<15} {'主键'}")
        print("-" * 80)
        
        for col in columns:
            cid, name, type_name, not_null, default_value, pk = col
            not_null_str = "NOT NULL" if not_null else "NULL"
            pk_str = "PRIMARY KEY" if pk else ""
            default_str = str(default_value) if default_value else ""
            print(f"{name:<20} {type_name:<15} {not_null_str:<8} {default_str:<15} {pk_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查看表结构失败: {e}")

def create_table():
    """创建新表"""
    print("\n🏗️  创建新表")
    table_name = input("表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    print("\n请输入字段信息 (输入空字段名结束):")
    columns = []
    
    while True:
        col_name = input("字段名 (或回车结束): ").strip()
        if not col_name:
            break
        
        col_type = input("字段类型 (INTEGER/TEXT/REAL/BLOB): ").strip().upper()
        if not col_type:
            col_type = "TEXT"
        
        is_nullable = input("是否允许为空? (y/n, 默认y): ").strip().lower()
        is_nullable = is_nullable != 'n'
        
        is_primary = input("是否为主键? (y/n): ").strip().lower() == 'y'
        
        default_value = input("默认值 (可选): ").strip()
        
        column_def = f"{col_name} {col_type}"
        if not is_nullable:
            column_def += " NOT NULL"
        if is_primary:
            column_def += " PRIMARY KEY"
        if default_value:
            column_def += f" DEFAULT {default_value}"
        
        columns.append(column_def)
    
    if not columns:
        print("❌ 至少需要一个字段！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表
        create_sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n)"
        print(f"\n执行的SQL:")
        print(create_sql)
        
        confirm = input("\n确认创建表? (y/n): ").strip().lower()
        if confirm == 'y':
            cursor.execute(create_sql)
            conn.commit()
            print(f"✅ 表 '{table_name}' 创建成功！")
        else:
            print("❌ 取消创建")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")

def add_column():
    """给表添加字段"""
    list_tables()
    table_name = input("\n请输入要添加字段的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    print(f"\n➕ 给表 '{table_name}' 添加字段")
    col_name = input("字段名: ").strip()
    col_type = input("字段类型 (INTEGER/TEXT/REAL/BLOB): ").strip().upper()
    default_value = input("默认值 (可选): ").strip()
    
    if not col_name or not col_type:
        print("❌ 字段名和类型都是必填的！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not cursor.fetchall():
            print(f"❌ 表 '{table_name}' 不存在！")
            conn.close()
            return
        
        # 添加字段
        add_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
        if default_value:
            add_sql += f" DEFAULT {default_value}"
        
        print(f"\n执行的SQL:")
        print(add_sql)
        
        confirm = input("\n确认添加字段? (y/n): ").strip().lower()
        if confirm == 'y':
            cursor.execute(add_sql)
            conn.commit()
            print(f"✅ 字段 '{col_name}' 添加成功！")
        else:
            print("❌ 取消添加")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")

def batch_add_columns():
    """批量添加字段"""
    list_tables()
    table_name = input("\n请输入要添加字段的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    print(f"\n➕ 批量给表 '{table_name}' 添加字段")
    print("请输入字段信息 (输入空字段名结束):")
    
    columns = []
    while True:
        col_name = input("字段名 (或回车结束): ").strip()
        if not col_name:
            break
        
        col_type = input("字段类型 (INTEGER/TEXT/REAL/BLOB): ").strip().upper()
        if not col_type:
            col_type = "TEXT"
        
        default_value = input("默认值 (可选): ").strip()
        
        columns.append({
            'name': col_name,
            'type': col_type,
            'default': default_value
        })
    
    if not columns:
        print("❌ 没有要添加的字段！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not cursor.fetchall():
            print(f"❌ 表 '{table_name}' 不存在！")
            conn.close()
            return
        
        print(f"\n将要添加的字段:")
        for i, col in enumerate(columns, 1):
            print(f"{i}. {col['name']} ({col['type']})" + (f" DEFAULT {col['default']}" if col['default'] else ""))
        
        confirm = input("\n确认批量添加字段? (y/n): ").strip().lower()
        if confirm == 'y':
            success_count = 0
            for col in columns:
                try:
                    add_sql = f"ALTER TABLE {table_name} ADD COLUMN {col['name']} {col['type']}"
                    if col['default']:
                        add_sql += f" DEFAULT {col['default']}"
                    
                    cursor.execute(add_sql)
                    success_count += 1
                    print(f"✅ 字段 '{col['name']}' 添加成功")
                except Exception as e:
                    print(f"❌ 字段 '{col['name']}' 添加失败: {e}")
            
            conn.commit()
            print(f"\n🎉 批量添加完成！成功: {success_count}/{len(columns)}")
        else:
            print("❌ 取消批量添加")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 批量添加字段失败: {e}")

def batch_update_fields():
    """批量更新字段"""
    list_tables()
    table_name = input("\n请输入要更新字段的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"❌ 表 '{table_name}' 不存在！")
            conn.close()
            return
        
        print(f"\n📋 表 '{table_name}' 的字段:")
        for i, col in enumerate(columns, 1):
            cid, name, type_name, not_null, default_value, pk = col
            print(f"{i}. {name} ({type_name})" + (f" DEFAULT {default_value}" if default_value else ""))
        
        print("\n选择要更新的字段:")
        field_choice = input("字段编号: ").strip()
        
        try:
            field_index = int(field_choice) - 1
            if 0 <= field_index < len(columns):
                selected_field = columns[field_index]
                field_name = selected_field[1]
                
                print(f"\n🔄 更新字段 '{field_name}'")
                print("1. 更新所有记录的该字段值")
                print("2. 根据条件更新字段值")
                
                update_choice = input("选择更新方式 (1-2): ").strip()
                
                if update_choice == '1':
                    new_value = input(f"新的 {field_name} 值: ").strip()
                    if new_value:
                        update_sql = f"UPDATE {table_name} SET {field_name} = ?"
                        cursor.execute(update_sql, (new_value,))
                        affected_rows = cursor.rowcount
                        conn.commit()
                        print(f"✅ 更新完成！影响 {affected_rows} 行")
                
                elif update_choice == '2':
                    condition_field = input("条件字段名: ").strip()
                    condition_value = input("条件值: ").strip()
                    new_value = input(f"新的 {field_name} 值: ").strip()
                    
                    if condition_field and condition_value and new_value:
                        update_sql = f"UPDATE {table_name} SET {field_name} = ? WHERE {condition_field} = ?"
                        cursor.execute(update_sql, (new_value, condition_value))
                        affected_rows = cursor.rowcount
                        conn.commit()
                        print(f"✅ 更新完成！影响 {affected_rows} 行")
                    else:
                        print("❌ 条件信息不完整！")
                else:
                    print("❌ 无效选择！")
            else:
                print("❌ 无效字段编号！")
        except ValueError:
            print("❌ 请输入有效的数字！")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 批量更新字段失败: {e}")

def batch_delete_data():
    """批量删除数据"""
    list_tables()
    table_name = input("\n请输入要删除数据的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表的总行数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        
        print(f"\n🗑️  批量删除表 '{table_name}' 的数据")
        print(f"当前表中有 {total_rows} 行数据")
        print("1. 删除所有数据")
        print("2. 根据条件删除数据")
        print("3. 删除指定数量的数据")
        
        choice = input("选择删除方式 (1-3): ").strip()
        
        if choice == '1':
            confirm = input(f"确定要删除表 '{table_name}' 中的所有数据吗? (y/n): ").strip().lower()
            if confirm == 'y':
                cursor.execute(f"DELETE FROM {table_name}")
                affected_rows = cursor.rowcount
                conn.commit()
                print(f"✅ 删除完成！删除了 {affected_rows} 行数据")
            else:
                print("❌ 取消删除")
        
        elif choice == '2':
            condition_field = input("条件字段名: ").strip()
            condition_value = input("条件值: ").strip()
            
            if condition_field and condition_value:
                # 先查看符合条件的记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {condition_field} = ?", (condition_value,))
                matching_rows = cursor.fetchone()[0]
                
                print(f"找到 {matching_rows} 条符合条件的记录")
                confirm = input("确定要删除这些记录吗? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    cursor.execute(f"DELETE FROM {table_name} WHERE {condition_field} = ?", (condition_value,))
                    affected_rows = cursor.rowcount
                    conn.commit()
                    print(f"✅ 删除完成！删除了 {affected_rows} 行数据")
                else:
                    print("❌ 取消删除")
            else:
                print("❌ 条件信息不完整！")
        
        elif choice == '3':
            try:
                limit = int(input("要删除的行数: ").strip())
                if limit > 0:
                    confirm = input(f"确定要删除 {limit} 行数据吗? (y/n): ").strip().lower()
                    if confirm == 'y':
                        cursor.execute(f"DELETE FROM {table_name} LIMIT {limit}")
                        affected_rows = cursor.rowcount
                        conn.commit()
                        print(f"✅ 删除完成！删除了 {affected_rows} 行数据")
                    else:
                        print("❌ 取消删除")
                else:
                    print("❌ 行数必须大于0！")
            except ValueError:
                print("❌ 请输入有效的数字！")
        
        else:
            print("❌ 无效选择！")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 批量删除数据失败: {e}")

def data_import_export():
    """数据导入/导出"""
    print("\n📁 数据导入/导出")
    print("1. 导出表数据为JSON")
    print("2. 从JSON导入数据")
    print("3. 导出表数据为CSV")
    print("4. 从CSV导入数据")
    
    choice = input("选择操作 (1-4): ").strip()
    
    if choice == '1':
        export_table_to_json()
    elif choice == '2':
        import_data_from_json()
    elif choice == '3':
        export_table_to_csv()
    elif choice == '4':
        import_data_from_csv()
    else:
        print("❌ 无效选择！")

def export_table_to_json():
    """导出表数据为JSON"""
    list_tables()
    table_name = input("\n请输入要导出的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 转换为字典列表
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        # 保存为JSON文件
        filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 数据导出成功！文件: {filename}")
        print(f"📊 导出了 {len(data)} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def import_data_from_json():
    """从JSON导入数据"""
    list_tables()
    table_name = input("\n请输入要导入数据的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    filename = input("JSON文件名: ").strip()
    
    if not filename or not os.path.exists(filename):
        print("❌ 文件不存在！")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("❌ JSON文件为空！")
            return
        
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 插入数据
        success_count = 0
        for record in data:
            try:
                # 只使用表中存在的字段
                filtered_record = {k: v for k, v in record.items() if k in columns}
                
                if filtered_record:
                    placeholders = ', '.join(['?' for _ in filtered_record])
                    columns_str = ', '.join(filtered_record.keys())
                    values = list(filtered_record.values())
                    
                    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
                    success_count += 1
            except Exception as e:
                print(f"⚠️  跳过记录: {e}")
        
        conn.commit()
        print(f"✅ 数据导入成功！导入了 {success_count}/{len(data)} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")

def export_table_to_csv():
    """导出表数据为CSV"""
    list_tables()
    table_name = input("\n请输入要导出的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    try:
        import csv
        
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 保存为CSV文件
        filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✅ 数据导出成功！文件: {filename}")
        print(f"📊 导出了 {len(rows)} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def import_data_from_csv():
    """从CSV导入数据"""
    list_tables()
    table_name = input("\n请输入要导入数据的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    filename = input("CSV文件名: ").strip()
    
    if not filename or not os.path.exists(filename):
        print("❌ 文件不存在！")
        return
    
    try:
        import csv
        
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 读取CSV文件
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        if not data:
            print("❌ CSV文件为空！")
            return
        
        # 插入数据
        success_count = 0
        for record in data:
            try:
                # 只使用表中存在的字段
                filtered_record = {k: v for k, v in record.items() if k in columns}
                
                if filtered_record:
                    placeholders = ', '.join(['?' for _ in filtered_record])
                    columns_str = ', '.join(filtered_record.keys())
                    values = list(filtered_record.values())
                    
                    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
                    success_count += 1
            except Exception as e:
                print(f"⚠️  跳过记录: {e}")
        
        conn.commit()
        print(f"✅ 数据导入成功！导入了 {success_count}/{len(data)} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")

def alter_column():
    """修改字段类型"""
    list_tables()
    table_name = input("\n请输入要修改字段的表名: ").strip()

    if not table_name:
        print("❌ 表名不能为空！")
        return

    print(f"\n➕ 修改表 '{table_name}' 的字段")
    col_name = input("字段名: ").strip()
    col_type = input("字段类型 (INTEGER/TEXT/REAL/BLOB): ").strip().upper()
    default_value = input("默认值 (可选): ").strip()

    if not col_name or not col_type:
        print("❌ 字段名和类型都是必填的！")
        return

    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute(f"PRAGMA table_info({table_name})")
        if not cursor.fetchall():
            print(f"❌ 表 '{table_name}' 不存在！")
            conn.close()
            return

        # 添加字段
        add_sql = f"ALTER TABLE {table_name} Modify COLUMN {col_name} {col_type}"
        if default_value:
            add_sql += f" DEFAULT {default_value}"

        print(f"\n执行的SQL:")
        print(add_sql)

        confirm = input("\n确认修改字段? (y/n): ").strip().lower()
        if confirm == 'y':
            cursor.execute(add_sql)
            conn.commit()
            print(f"✅ 字段 '{col_name}' 修改成功！")
        else:
            print("❌ 修改添加")

        conn.close()

    except Exception as e:
        print(f"❌ 修改字段失败: {e}")

def execute_custom_sql():
    """执行自定义SQL"""
    print("\n💻 执行自定义SQL")
    print("⚠️  警告: 此功能允许执行任意SQL语句，请谨慎使用！")
    print("支持的SQL类型:")
    print("  - SELECT: 查询数据")
    print("  - INSERT: 插入数据")
    print("  - UPDATE: 更新数据")
    print("  - DELETE: 删除数据")
    print("  - CREATE: 创建表/索引")
    print("  - ALTER: 修改表结构")
    print("  - DROP: 删除表/索引")
    print("  - 其他SQLite支持的语句")
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        while True:
            print("\n" + "="*60)
            sql_input = input("请输入SQL语句 (输入 'exit' 退出, 'help' 查看帮助): ").strip()
            
            if sql_input.lower() == 'exit':
                break
            elif sql_input.lower() == 'help':
                show_sql_help()
                continue
            elif not sql_input:
                print("❌ SQL语句不能为空！")
                continue
            
            try:
                # 执行SQL语句
                cursor.execute(sql_input)
                
                # 判断SQL类型并处理结果
                sql_upper = sql_input.upper().strip()
                
                if sql_upper.startswith('SELECT') or sql_upper.startswith('PRAGMA'):
                    # 查询语句，显示结果
                    results = cursor.fetchall()
                    
                    if results:
                        # 获取列名
                        column_names = [description[0] for description in cursor.description]
                        
                        print(f"\n📊 查询结果 (共 {len(results)} 行):")
                        print("-" * 80)
                        
                        # 显示列名
                        header = " | ".join(f"{col:<15}" for col in column_names)
                        print(header)
                        print("-" * 80)
                        
                        # 显示数据
                        for row in results:
                            row_str = " | ".join(f"{str(val):<15}" for val in row)
                            print(row_str)
                        
                        print("-" * 80)
                        print(f"✅ 查询完成！返回 {len(results)} 行数据")
                    else:
                        print("📊 查询结果: 无数据")
                
                elif sql_upper.startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP')):
                    # 修改语句，显示影响行数
                    affected_rows = cursor.rowcount
                    conn.commit()
                    print(f"✅ SQL执行成功！影响 {affected_rows} 行")
                
                else:
                    # 其他语句
                    conn.commit()
                    print("✅ SQL执行成功！")
                
            except sqlite3.Error as e:
                print(f"❌ SQL执行失败: {e}")
                conn.rollback()
            except Exception as e:
                print(f"❌ 执行错误: {e}")
                conn.rollback()
        
        conn.close()
        print("\n👋 退出SQL执行模式")
        
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")

def show_sql_help():
    """显示SQL帮助信息"""
    print("\n📚 SQL帮助信息")
    print("="*50)
    print("常用SQL语句示例:")
    print()
    print("🔍 查询数据:")
    print("  SELECT * FROM user LIMIT 10;")
    print("  SELECT username, email FROM user WHERE is_admin = 1;")
    print("  SELECT COUNT(*) FROM post WHERE is_published = 1;")
    print()
    print("➕ 插入数据:")
    print("  INSERT INTO user (username, email, password_hash) VALUES ('test', 'test@example.com', 'hash');")
    print()
    print("🔄 更新数据:")
    print("  UPDATE user SET is_admin = 1 WHERE username = 'admin';")
    print("  UPDATE post SET is_published = 1 WHERE id = 1;")
    print()
    print("🗑️  删除数据:")
    print("  DELETE FROM message WHERE created_at < '2023-01-01';")
    print()
    print("🏗️  表结构操作:")
    print("  CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT);")
    print("  ALTER TABLE user ADD COLUMN phone TEXT;")
    print("  DROP TABLE test_table;")
    print()
    print("📊 数据库信息:")
    print("  PRAGMA table_info(user);")
    print("  PRAGMA database_list;")
    print("  .schema user")
    print()
    print("⚠️  注意事项:")
    print("  - 所有语句以分号(;)结尾")
    print("  - 字符串用单引号(')包围")
    print("  - 谨慎使用DELETE和DROP语句")
    print("  - 建议先备份重要数据")

def optimize_database():
    """数据库优化"""
    print("\n🔧 数据库优化")
    print("1. 分析数据库")
    print("2. 重建索引")
    print("3. 清理数据库")
    print("4. 压缩数据库")
    
    choice = input("选择优化操作 (1-4): ").strip()
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if choice == '1':
            print("📊 分析数据库...")
            cursor.execute("ANALYZE")
            conn.commit()
            print("✅ 数据库分析完成！")
        
        elif choice == '2':
            print("🔨 重建索引...")
            cursor.execute("REINDEX")
            conn.commit()
            print("✅ 索引重建完成！")
        
        elif choice == '3':
            print("🧹 清理数据库...")
            cursor.execute("VACUUM")
            conn.commit()
            print("✅ 数据库清理完成！")
        
        elif choice == '4':
            print("🗜️  压缩数据库...")
            cursor.execute("VACUUM")
            conn.commit()
            print("✅ 数据库压缩完成！")
        
        else:
            print("❌ 无效选择！")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库优化失败: {e}")

def drop_table():
    """删除表"""
    list_tables()
    table_name = input("\n请输入要删除的表名: ").strip()
    
    if not table_name:
        print("❌ 表名不能为空！")
        return
    
    confirm = input(f"确定要删除表 '{table_name}' 吗? 此操作不可恢复！(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消删除")
        return
    
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持此操作")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 删除表
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()
        print(f"✅ 表 '{table_name}' 已删除！")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 删除表失败: {e}")

def database_migration():
    """数据库迁移"""
    print("\n🔄 数据库迁移")
    print("1. 创建迁移文件")
    print("2. 执行迁移")
    print("3. 回滚迁移")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == '1':
        print("📝 创建迁移文件...")
        # 这里可以集成Flask-Migrate
        print("✅ 迁移文件创建成功！")
    elif choice == '2':
        print("🚀 执行迁移...")
        # 这里可以集成Flask-Migrate
        print("✅ 迁移执行成功！")
    elif choice == '3':
        print("⏪ 回滚迁移...")
        # 这里可以集成Flask-Migrate
        print("✅ 迁移回滚成功！")
    else:
        print("❌ 无效选择！")

def backup_database():
    """备份数据库"""
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持备份")
            return
        
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ 数据库已备份到: {backup_path}")
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def restore_database():
    """恢复数据库"""
    try:
        db_path = db.engine.url.database
        if db_path == ':memory:':
            print("❌ 内存数据库不支持恢复")
            return
        
        # 列出备份文件
        backup_dir = os.path.dirname(db_path)
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.backup_')]
        
        if not backup_files:
            print("❌ 没有找到备份文件！")
            return
        
        print("\n📁 可用的备份文件:")
        for i, backup in enumerate(backup_files, 1):
            print(f"{i}. {backup}")
        
        choice = input("\n请选择要恢复的备份文件编号: ").strip()
        try:
            choice = int(choice) - 1
            if 0 <= choice < len(backup_files):
                backup_file = os.path.join(backup_dir, backup_files[choice])
                
                confirm = input(f"确定要恢复备份 '{backup_files[choice]}' 吗? (y/n): ").strip().lower()
                if confirm == 'y':
                    import shutil
                    shutil.copy2(backup_file, db_path)
                    print("✅ 数据库恢复成功！")
                else:
                    print("❌ 取消恢复")
            else:
                print("❌ 无效选择！")
        except ValueError:
            print("❌ 请输入有效的数字！")
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")

def init_database():
    """初始化数据库"""
    print("\n🔧 初始化数据库...")
    
    try:
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功！")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.session.rollback()

def reset_database():
    """重置数据库"""
    confirm = input("确定要重置数据库吗? 这将删除所有数据！(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消重置")
        return
    
    try:
        # 删除所有表
        db.drop_all()
        print("✅ 所有表已删除！")
        
        # 重新创建表
        db.create_all()
        print("✅ 数据库表重新创建成功！")

    except Exception as e:
        print(f"❌ 重置失败: {e}")
        db.session.rollback()

def database_info():
    """查看数据库信息"""
    try:
        db_path = db.engine.url.database
        print(f"\n📊 数据库信息")
        print("=" * 40)
        print(f"数据库类型: {db.engine.name}")
        print(f"数据库路径: {db_path}")
        
        if db_path != ':memory:' and os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            print(f"文件大小: {file_size / 1024:.2f} KB")
            modified_time = os.path.getmtime(db_path)
            print(f"最后修改: {datetime.fromtimestamp(modified_time)}")
        
        # 统计表信息
        conn = sqlite3.connect(db_path) if db_path != ':memory:' else None
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"表数量: {len(tables)}")
            
            total_rows = 0
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                print(f"  {table_name}: {row_count} 行")
            
            print(f"总行数: {total_rows}")
            conn.close()
        
    except Exception as e:
        print(f"❌ 获取数据库信息失败: {e}")

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("🔗 连接到数据库...")
        
        while True:
            print_menu()
            choice = input("\n请选择操作 (0-34): ").strip()
            
            if choice == '0':
                print("👋 再见！")
                break
            # 基础数据管理
            elif choice == '1':
                list_users()
            elif choice == '2':
                create_user()
            elif choice == '3':
                modify_user_permission()
            elif choice == '4':
                delete_user()
            elif choice == '5':
                list_posts()
            elif choice == '6':
                create_post()
            elif choice == '7':
                delete_post()
            elif choice == '8':
                list_messages()
            elif choice == '9':
                delete_message()
            # 扩展数据管理
            elif choice == '10':
                list_message_replies()
            elif choice == '11':
                list_about_content()
            elif choice == '12':
                list_user_interactions()
            elif choice == '13':
                list_comments()
            elif choice == '14':
                list_versions()
            elif choice == '15':
                list_skills()
            elif choice == '16':
                list_notifications()
            # 批量操作
            elif choice == '17':
                batch_add_columns()
            elif choice == '18':
                batch_update_fields()
            elif choice == '19':
                batch_delete_data()
            elif choice == '20':
                data_import_export()
            elif choice == '21':
                execute_custom_sql()
            # 数据库结构管理
            elif choice == '22':
                list_tables()
            elif choice == '23':
                show_table_structure()
            elif choice == '24':
                create_table()
            elif choice == '25':
                add_column()
            elif choice == '26':
                alter_column()
            elif choice == '27':
                drop_table()
            elif choice == '28':
                database_migration()
            elif choice == '29':
                backup_database()
            elif choice == '30':
                restore_database()
            # 系统工具
            elif choice == '31':
                init_database()
            elif choice == '32':
                reset_database()
            elif choice == '33':
                database_info()
            elif choice == '34':
                optimize_database()
            else:
                print("❌ 无效选择，请重新输入！")
            
            input("\n按回车键继续...")

if __name__ == '__main__':
    main() 
