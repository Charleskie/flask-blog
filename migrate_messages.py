#!/usr/bin/env python3
"""
消息数据库迁移脚本
用于创建Message表并添加示例数据
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Message, User

def migrate_messages():
    """执行消息数据库迁移"""
    print("🔄 开始消息数据库迁移...")
    
    with app.app_context():
        try:
            # 检查是否需要创建新表
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'message' not in existing_tables:
                print("📝 创建Message表...")
                db.create_all()
                print("✅ Message表创建成功")
            else:
                print("📋 Message表已存在")
            
            # 创建示例消息（如果没有消息）
            messages = Message.query.all()
            if not messages:
                print("📝 创建示例消息...")
                
                # 创建示例消息
                sample_messages = [
                    {
                        'name': '张三',
                        'email': 'zhangsan@example.com',
                        'subject': '关于网站功能的建议',
                        'message': '''您好！

我很喜欢您的个人网站设计，界面简洁美观。我想提出一些建议：

1. 希望可以添加更多的项目展示
2. 博客文章的分类功能很实用
3. 建议添加搜索功能

期待您的回复！

祝好，
张三''',
                        'status': 'unread',
                        'ip_address': '192.168.1.100',
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    {
                        'name': '李四',
                        'email': 'lisi@example.com',
                        'subject': '技术合作咨询',
                        'message': '''您好！

我是某公司的技术负责人，看了您的项目展示，对您的技术能力很感兴趣。

我们公司正在寻找有经验的开发者参与一个Web应用项目，想了解您是否有兴趣合作？

项目详情：
- 技术栈：Python + Flask + Vue.js
- 开发周期：3-6个月
- 工作方式：远程协作

期待您的回复！

李四
技术负责人
某科技有限公司''',
                        'status': 'read',
                        'ip_address': '203.208.60.1',
                        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    },
                    {
                        'name': '王五',
                        'email': 'wangwu@example.com',
                        'subject': '学习交流',
                        'message': '''您好！

我是一名在校学生，正在学习Web开发。看了您的博客文章，收获很多！

有几个问题想请教：
1. 您是如何学习Flask框架的？
2. 有什么好的学习资源推荐吗？
3. 对于初学者有什么建议？

谢谢！

王五
计算机科学专业学生''',
                        'status': 'replied',
                        'ip_address': '114.88.200.1',
                        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
                    },
                    {
                        'name': '赵六',
                        'email': 'zhaoliu@example.com',
                        'subject': '网站访问问题',
                        'message': '''您好！

我在访问您的网站时遇到了一些问题：
1. 在移动设备上，某些页面显示不正常
2. 加载速度比较慢
3. 搜索功能有时无响应

希望您能检查一下这些问题。

谢谢！

赵六''',
                        'status': 'archived',
                        'ip_address': '180.168.1.1',
                        'user_agent': 'Mozilla/5.0 (Android 10; Mobile) AppleWebKit/537.36'
                    }
                ]
                
                for message_data in sample_messages:
                    message = Message(
                        name=message_data['name'],
                        email=message_data['email'],
                        subject=message_data['subject'],
                        message=message_data['message'],
                        status=message_data['status'],
                        ip_address=message_data['ip_address'],
                        user_agent=message_data['user_agent']
                    )
                    db.session.add(message)
                
                db.session.commit()
                print("✅ 示例消息创建完成")
            else:
                print(f"📋 已有 {len(messages)} 条消息")
            
            print("🎉 消息数据库迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_messages() 