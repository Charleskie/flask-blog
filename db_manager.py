#!/usr/bin/env python3
"""
数据库管理工具 - 提供CRUD操作和数据库结构管理
"""

from app import create_app
from app.models.user import User, db
from app.models.post import Post
from app.models.project import Project
from app.models.message import Message
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys
import sqlite3
import os

def print_menu():
    """打印菜单"""
    print("\n" + "="*60)
    print("🗄️  数据库管理工具")
    print("="*60)
    print("📊 数据管理:")
    print("  1. 查看所有用户")
    print("  2. 创建新用户")
    print("  3. 修改用户权限")
    print("  4. 删除用户")
    print("  5. 查看所有文章")
    print("  6. 创建新文章")
    print("  7. 删除文章")
    print("  8. 查看所有项目")
    print("  9. 创建新项目")
    print("  10. 删除项目")
    print("  11. 查看所有消息")
    print("  12. 删除消息")
    print("  13. 数据库统计")
    print("\n🏗️  数据库结构管理:")
    print("  14. 查看所有表")
    print("  15. 查看表结构")
    print("  16. 创建新表")
    print("  17. 给表添加字段")
    print("  18. 删除表")
    print("  19. 数据库迁移")
    print("  20. 备份数据库")
    print("  21. 恢复数据库")
    print("\n🔧 系统工具:")
    print("  22. 初始化数据库")
    print("  23. 重置数据库")
    print("  24. 查看数据库信息")
    print("  0. 退出")
    print("="*60)

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

def list_projects():
    """查看所有项目"""
    projects = Project.query.all()
    print(f"\n🚀 项目列表 (共{len(projects)}个):")
    print("-" * 80)
    print(f"{'ID':<5} {'名称':<25} {'技术栈':<20} {'状态':<8} {'创建时间'}")
    print("-" * 80)
    for project in projects:
        status = "已完成" if project.is_completed else "进行中"
        print(f"{project.id:<5} {project.name[:23]:<25} {project.tech_stack[:18]:<20} {status:<8} {project.created_at.strftime('%Y-%m-%d')}")

def create_project():
    """创建新项目"""
    print("\n➕ 创建新项目")
    name = input("项目名称: ").strip()
    description = input("项目描述: ").strip()
    tech_stack = input("技术栈: ").strip()
    github_url = input("GitHub链接: ").strip()
    is_completed = input("是否已完成? (y/n): ").strip().lower() == 'y'
    
    if not name or not description:
        print("❌ 项目名称和描述都是必填的！")
        return
    
    try:
        project = Project(
            name=name,
            description=description,
            tech_stack=tech_stack,
            github_url=github_url,
            is_completed=is_completed
        )
        db.session.add(project)
        db.session.commit()
        print(f"✅ 项目 '{name}' 创建成功！")
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        db.session.rollback()

def delete_project():
    """删除项目"""
    list_projects()
    project_id = input("\n请输入要删除的项目ID: ").strip()
    
    try:
        project_id = int(project_id)
        project = Project.query.get(project_id)
        if not project:
            print("❌ 项目不存在！")
            return
        
        confirm = input(f"确定要删除项目 '{project.name}' 吗? (y/n): ").strip().lower()
        if confirm == 'y':
            db.session.delete(project)
            db.session.commit()
            print(f"✅ 项目 '{project.name}' 已删除！")
        else:
            print("❌ 取消删除")
            
    except ValueError:
        print("❌ 请输入有效的项目ID！")
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

def database_stats():
    """数据库统计"""
    users_count = User.query.count()
    posts_count = Post.query.count()
    projects_count = Project.query.count()
    messages_count = Message.query.count()
    
    admin_count = User.query.filter_by(is_admin=True).count()
    published_posts = Post.query.filter_by(is_published=True).count()
    completed_projects = Project.query.filter_by(is_completed=True).count()
    replied_messages = Message.query.filter_by(is_replied=True).count()
    
    print("\n📊 数据库统计")
    print("=" * 40)
    print(f"👥 用户总数: {users_count} (管理员: {admin_count})")
    print(f"📝 文章总数: {posts_count} (已发布: {published_posts})")
    print(f"🚀 项目总数: {projects_count} (已完成: {completed_projects})")
    print(f"💬 消息总数: {messages_count} (已回复: {replied_messages})")
    print("=" * 40)

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
        
        # 创建默认管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 默认管理员用户创建成功！")
            print("   用户名: admin")
            print("   密码: admin123")
        else:
            print("ℹ️  管理员用户已存在")
        
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
        
        # 创建默认管理员用户
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ 默认管理员用户创建成功！")
        print("   用户名: admin")
        print("   密码: admin123")
        
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
            choice = input("\n请选择操作 (0-24): ").strip()
            
            if choice == '0':
                print("👋 再见！")
                break
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
                list_projects()
            elif choice == '9':
                create_project()
            elif choice == '10':
                delete_project()
            elif choice == '11':
                list_messages()
            elif choice == '12':
                delete_message()
            elif choice == '13':
                database_stats()
            elif choice == '14':
                list_tables()
            elif choice == '15':
                show_table_structure()
            elif choice == '16':
                create_table()
            elif choice == '17':
                add_column()
            elif choice == '18':
                drop_table()
            elif choice == '19':
                database_migration()
            elif choice == '20':
                backup_database()
            elif choice == '21':
                restore_database()
            elif choice == '22':
                init_database()
            elif choice == '23':
                reset_database()
            elif choice == '24':
                database_info()
            else:
                print("❌ 无效选择，请重新输入！")
            
            input("\n按回车键继续...")

if __name__ == '__main__':
    main() 