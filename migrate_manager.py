#!/usr/bin/env python3
"""
数据库迁移管理工具 - 基于Flask-Migrate
"""

import os
import sys
from datetime import datetime
from app import create_app
from app.models.user import db

def print_menu():
    """打印菜单"""
    print("\n" + "="*60)
    print("🔄 数据库迁移管理工具")
    print("="*60)
    print("📝 迁移操作:")
    print("  1. 初始化迁移环境")
    print("  2. 创建迁移文件")
    print("  3. 查看迁移历史")
    print("  4. 执行迁移")
    print("  5. 回滚迁移")
    print("  6. 升级到指定版本")
    print("  7. 降级到指定版本")
    print("  8. 显示当前版本")
    print("  9. 显示迁移信息")
    print("\n🔧 数据库操作:")
    print("  10. 初始化数据库")
    print("  11. 重置数据库")
    print("  12. 备份数据库")
    print("  13. 恢复数据库")
    print("  14. 查看数据库状态")
    print("\n📊 数据管理:")
    print("  15. 查看所有表")
    print("  16. 查看表结构")
    print("  17. 创建新表")
    print("  18. 给表添加字段")
    print("  19. 删除表")
    print("  0. 退出")
    print("="*60)

def init_migration():
    """初始化迁移环境"""
    print("\n🔧 初始化迁移环境...")
    
    try:
        # 检查是否已初始化
        if os.path.exists('migrations'):
            print("ℹ️  迁移环境已存在")
            return
        
        # 创建迁移目录
        os.makedirs('migrations', exist_ok=True)
        print("✅ 迁移目录创建成功")
        
        # 这里应该调用 flask db init
        print("📝 请运行以下命令初始化迁移环境:")
        print("   flask db init")
        print("   flask db migrate -m 'Initial migration'")
        print("   flask db upgrade")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

def create_migration():
    """创建迁移文件"""
    print("\n📝 创建迁移文件...")
    
    message = input("请输入迁移描述: ").strip()
    if not message:
        message = f"Migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # 这里应该调用 flask db migrate -m message
        print(f"📝 请运行以下命令创建迁移:")
        print(f"   flask db migrate -m '{message}'")
        
    except Exception as e:
        print(f"❌ 创建迁移失败: {e}")

def show_migration_history():
    """查看迁移历史"""
    print("\n📋 迁移历史...")
    
    try:
        # 这里应该调用 flask db history
        print("📝 请运行以下命令查看迁移历史:")
        print("   flask db history")
        
    except Exception as e:
        print(f"❌ 查看迁移历史失败: {e}")

def upgrade_database():
    """执行迁移"""
    print("\n🚀 执行迁移...")
    
    try:
        # 这里应该调用 flask db upgrade
        print("📝 请运行以下命令执行迁移:")
        print("   flask db upgrade")
        
    except Exception as e:
        print(f"❌ 执行迁移失败: {e}")

def downgrade_database():
    """回滚迁移"""
    print("\n⏪ 回滚迁移...")
    
    try:
        # 这里应该调用 flask db downgrade
        print("📝 请运行以下命令回滚迁移:")
        print("   flask db downgrade")
        
    except Exception as e:
        print(f"❌ 回滚迁移失败: {e}")

def upgrade_to_version():
    """升级到指定版本"""
    print("\n📈 升级到指定版本...")
    
    version = input("请输入目标版本号: ").strip()
    if not version:
        print("❌ 版本号不能为空！")
        return
    
    try:
        print(f"📝 请运行以下命令升级到版本 {version}:")
        print(f"   flask db upgrade {version}")
        
    except Exception as e:
        print(f"❌ 升级失败: {e}")

def downgrade_to_version():
    """降级到指定版本"""
    print("\n📉 降级到指定版本...")
    
    version = input("请输入目标版本号: ").strip()
    if not version:
        print("❌ 版本号不能为空！")
        return
    
    try:
        print(f"📝 请运行以下命令降级到版本 {version}:")
        print(f"   flask db downgrade {version}")
        
    except Exception as e:
        print(f"❌ 降级失败: {e}")

def show_current_version():
    """显示当前版本"""
    print("\n📊 当前版本...")
    
    try:
        print("📝 请运行以下命令查看当前版本:")
        print("   flask db current")
        
    except Exception as e:
        print(f"❌ 查看当前版本失败: {e}")

def show_migration_info():
    """显示迁移信息"""
    print("\n📋 迁移信息...")
    
    try:
        print("📝 请运行以下命令查看迁移信息:")
        print("   flask db show")
        
    except Exception as e:
        print(f"❌ 查看迁移信息失败: {e}")

def init_database():
    """初始化数据库"""
    print("\n🔧 初始化数据库...")
    
    try:
        app = create_app()
        with app.app_context():
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功！")
            
            # 创建默认管理员用户
            from app.models.user import User
            from werkzeug.security import generate_password_hash
            
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

def reset_database():
    """重置数据库"""
    confirm = input("确定要重置数据库吗? 这将删除所有数据！(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消重置")
        return
    
    try:
        app = create_app()
        with app.app_context():
            # 删除所有表
            db.drop_all()
            print("✅ 所有表已删除！")
            
            # 重新创建表
            db.create_all()
            print("✅ 数据库表重新创建成功！")
            
            # 创建默认管理员用户
            from app.models.user import User
            from werkzeug.security import generate_password_hash
            
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

def backup_database():
    """备份数据库"""
    try:
        app = create_app()
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print("❌ 数据库文件不存在！")
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
        app = create_app()
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
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

def show_database_status():
    """查看数据库状态"""
    try:
        app = create_app()
        with app.app_context():
            print("\n📊 数据库状态")
            print("=" * 40)
            
            # 检查数据库文件
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                modified_time = os.path.getmtime(db_path)
                print(f"数据库文件: {db_path}")
                print(f"文件大小: {file_size / 1024:.2f} KB")
                print(f"最后修改: {datetime.fromtimestamp(modified_time)}")
            else:
                print("❌ 数据库文件不存在")
                return
            
            # 检查表
            from app.models.user import User
            from app.models.post import Post
            from app.models.project import Project
            from app.models.message import Message
            
            tables = [User, Post, Project, Message]
            print(f"\n表状态:")
            for table in tables:
                count = table.query.count()
                print(f"  {table.__tablename__}: {count} 行")
        
    except Exception as e:
        print(f"❌ 查看数据库状态失败: {e}")

def list_tables():
    """查看所有表"""
    try:
        app = create_app()
        with app.app_context():
            import sqlite3
            
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print("❌ 数据库文件不存在！")
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"\n📋 数据库表列表 (共{len(tables)}个):")
            print("-" * 50)
            print(f"{'表名':<30} {'行数'}")
            print("-" * 50)
            
            for table in tables:
                table_name = table[0]
                # 获取表的行数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                print(f"{table_name:<30} {row_count}")
            
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
        app = create_app()
        with app.app_context():
            import sqlite3
            
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print("❌ 数据库文件不存在！")
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
        app = create_app()
        with app.app_context():
            import sqlite3
            
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print("❌ 数据库文件不存在！")
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
        app = create_app()
        with app.app_context():
            import sqlite3
            
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print("❌ 数据库文件不存在！")
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
        app = create_app()
        with app.app_context():
            import sqlite3
            
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if not os.path.exists(db_path):
                print("❌ 数据库文件不存在！")
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

def main():
    """主函数"""
    print("🔗 连接到数据库...")
    
    while True:
        print_menu()
        choice = input("\n请选择操作 (0-19): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        elif choice == '1':
            init_migration()
        elif choice == '2':
            create_migration()
        elif choice == '3':
            show_migration_history()
        elif choice == '4':
            upgrade_database()
        elif choice == '5':
            downgrade_database()
        elif choice == '6':
            upgrade_to_version()
        elif choice == '7':
            downgrade_to_version()
        elif choice == '8':
            show_current_version()
        elif choice == '9':
            show_migration_info()
        elif choice == '10':
            init_database()
        elif choice == '11':
            reset_database()
        elif choice == '12':
            backup_database()
        elif choice == '13':
            restore_database()
        elif choice == '14':
            show_database_status()
        elif choice == '15':
            list_tables()
        elif choice == '16':
            show_table_structure()
        elif choice == '17':
            create_table()
        elif choice == '18':
            add_column()
        elif choice == '19':
            drop_table()
        else:
            print("❌ 无效选择，请重新输入！")
        
        input("\n按回车键继续...")

if __name__ == '__main__':
    main() 