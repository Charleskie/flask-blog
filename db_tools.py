#!/usr/bin/env python3
"""
数据库工具统一入口
提供便捷的数据库管理功能
"""

import sys
import os
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("\n" + "="*70)
    print("🗄️  数据库管理工具套件")
    print("="*70)
    print("📦 可用工具:")
    print("  1. 基础数据库管理工具 (db_manager.py)")
    print("  2. 高级迁移管理工具 (migrate_manager.py)")
    print("  3. 快速初始化数据库")
    print("  4. 快速备份数据库")
    print("  5. 查看数据库状态")
    print("  6. 打开数据库文件")
    print("  0. 退出")
    print("="*70)

def quick_init_db():
    """快速初始化数据库"""
    print("\n🔧 快速初始化数据库...")
    
    try:
        from app import create_app
        from app.models.user import db, User
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        with app.app_context():
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功！")

        print("\n🎉 数据库初始化完成！")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

def quick_backup_db():
    """快速备份数据库"""
    print("\n💾 快速备份数据库...")
    
    try:
        from app import create_app
        import shutil
        
        app = create_app()
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print("❌ 数据库文件不存在！")
            return
        
        # 创建备份目录
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"database_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # 执行备份
        shutil.copy2(db_path, backup_path)
        
        # 显示备份信息
        file_size = os.path.getsize(backup_path)
        print(f"✅ 数据库已备份到: {backup_path}")
        print(f"📁 备份文件大小: {file_size / 1024:.2f} KB")
        print(f"🕒 备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def show_db_status():
    """查看数据库状态"""
    print("\n📊 数据库状态...")
    
    try:
        from app import create_app
        from app.models.user import User
        from app.models.post import Post
        from app.models.project import Project
        from app.models.message import Message
        
        app = create_app()
        with app.app_context():
            # 检查数据库文件
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                modified_time = os.path.getmtime(db_path)
                
                print("=" * 50)
                print("📁 数据库文件信息:")
                print(f"   路径: {db_path}")
                print(f"   大小: {file_size / 1024:.2f} KB")
                print(f"   修改时间: {datetime.fromtimestamp(modified_time)}")
                print("=" * 50)
                
                # 统计表信息
                tables = [User, Post, Project, Message]
                print("\n📋 表统计信息:")
                total_rows = 0
                
                for table in tables:
                    try:
                        count = table.query.count()
                        total_rows += count
                        print(f"   {table.__tablename__}: {count} 行")
                    except Exception as e:
                        print(f"   {table.__tablename__}: 表不存在或出错")
                
                print(f"\n📊 总计: {total_rows} 行数据")
                
            else:
                print("❌ 数据库文件不存在")
                print("💡 建议运行快速初始化数据库功能")
        
    except Exception as e:
        print(f"❌ 查看数据库状态失败: {e}")

def open_db_file():
    """打开数据库文件"""
    print("\n🔍 打开数据库文件...")
    
    try:
        from app import create_app
        
        app = create_app()
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print("❌ 数据库文件不存在！")
            return
        
        # 尝试使用系统默认应用打开
        import subprocess
        import platform
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(["open", db_path])
            print(f"✅ 已在默认应用中打开: {db_path}")
        elif system == "Windows":
            subprocess.run(["start", db_path], shell=True)
            print(f"✅ 已在默认应用中打开: {db_path}")
        elif system == "Linux":
            subprocess.run(["xdg-open", db_path])
            print(f"✅ 已在默认应用中打开: {db_path}")
        else:
            print(f"📁 数据库文件位置: {db_path}")
            print("💡 请手动使用数据库查看器打开此文件")
        
    except Exception as e:
        print(f"❌ 打开数据库文件失败: {e}")

def run_db_manager():
    """运行基础数据库管理工具"""
    print("\n🚀 启动基础数据库管理工具...")
    os.system("python3 db_manager.py")

def run_migrate_manager():
    """运行高级迁移管理工具"""
    print("\n🚀 启动高级迁移管理工具...")
    os.system("python3 migrate_manager.py")

def main():
    """主函数"""
    print("🔗 连接到数据库...")
    
    while True:
        print_banner()
        choice = input("\n请选择工具 (0-6): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            run_db_manager()
        elif choice == '2':
            run_migrate_manager()
        elif choice == '3':
            quick_init_db()
        elif choice == '4':
            quick_backup_db()
        elif choice == '5':
            show_db_status()
        elif choice == '6':
            open_db_file()
        else:
            print("❌ 无效选择，请重新输入！")
        
        input("\n按回车键继续...")

if __name__ == '__main__':
    main() 