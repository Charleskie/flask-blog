#!/usr/bin/env python3
"""
数据库管理工具 - 提供CRUD操作
"""

from app import create_app
from app.models.user import User, db
from app.models.post import Post
from app.models.project import Project
from app.models.message import Message
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys

def print_menu():
    """打印菜单"""
    print("\n" + "="*50)
    print("🗄️  数据库管理工具")
    print("="*50)
    print("1. 查看所有用户")
    print("2. 创建新用户")
    print("3. 修改用户权限")
    print("4. 删除用户")
    print("5. 查看所有文章")
    print("6. 创建新文章")
    print("7. 删除文章")
    print("8. 查看所有项目")
    print("9. 创建新项目")
    print("10. 删除项目")
    print("11. 查看所有消息")
    print("12. 删除消息")
    print("13. 数据库统计")
    print("0. 退出")
    print("="*50)

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

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("🔗 连接到数据库...")
        
        while True:
            print_menu()
            choice = input("\n请选择操作 (0-13): ").strip()
            
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
            else:
                print("❌ 无效选择，请重新输入！")
            
            input("\n按回车键继续...")

if __name__ == '__main__':
    main() 