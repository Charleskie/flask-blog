#!/usr/bin/env python3
"""
测试脚本
用于验证Flask应用的基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    try:
        from app import app, db, User, Post, Project
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    try:
        from app import app, db
        
        with app.app_context():
            # 创建数据库表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = ['user', 'post', 'project']
            
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 表 {table} 存在")
                else:
                    print(f"❌ 表 {table} 不存在")
            
            return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_routes():
    """测试路由"""
    try:
        from app import app
        
        # 测试主要路由
        routes_to_test = [
            '/',
            '/about',
            '/projects',
            '/blog',
            '/contact',
            '/login',
            '/register',
            '/forgot-password'
        ]
        
        with app.test_client() as client:
            for route in routes_to_test:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✅ 路由 {route} 正常")
                else:
                    print(f"❌ 路由 {route} 返回状态码 {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ 路由测试失败: {e}")
        return False

def test_user_registration():
    """测试用户注册功能"""
    try:
        from app import app, db, User
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # 清理测试用户
            test_user = User.query.filter_by(username='testuser').first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
            
            # 创建测试用户
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass123')
            )
            db.session.add(test_user)
            db.session.commit()
            
            # 验证用户创建
            created_user = User.query.filter_by(username='testuser').first()
            if created_user:
                print("✅ 用户注册功能正常")
                
                # 清理测试用户
                db.session.delete(created_user)
                db.session.commit()
                return True
            else:
                print("❌ 用户注册功能异常")
                return False
    except Exception as e:
        print(f"❌ 用户注册测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试Flask个人网站应用...")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("数据库连接", test_database),
        ("路由测试", test_routes),
        ("用户注册", test_user_registration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用可以正常运行。")
        print("\n📝 下一步:")
        print("1. 运行 'python run.py' 启动应用")
        print("2. 访问 http://localhost:5000")
        print("3. 注册新用户并测试功能")
    else:
        print("⚠️  部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 