# 项目结构说明

## 📁 目录结构

```
my_web/
├── app/                          # 主应用包
│   ├── __init__.py              # 应用工厂
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户模型
│   │   ├── post.py             # 文章模型
│   │   ├── project.py          # 项目模型
│   │   └── message.py          # 消息模型
│   ├── routes/                  # 路由模块
│   │   ├── __init__.py
│   │   ├── main.py             # 主要页面路由
│   │   ├── admin.py            # 管理后台路由
│   │   └── auth.py             # 认证路由
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   └── filters.py          # 自定义过滤器
│   ├── templates/               # 模板文件
│   │   ├── base.html           # 基础模板
│   │   ├── frontend/           # 前台页面模板
│   │   │   ├── index.html
│   │   │   ├── about.html
│   │   │   ├── projects.html
│   │   │   ├── project_detail.html
│   │   │   ├── blog.html
│   │   │   ├── post_detail.html
│   │   │   └── contact.html
│   │   ├── admin/              # 管理后台模板
│   │   │   ├── admin.html
│   │   │   ├── admin_posts.html
│   │   │   ├── new_post.html
│   │   │   ├── edit_post.html
│   │   │   ├── admin_projects.html
│   │   │   ├── new_project.html
│   │   │   ├── edit_project.html
│   │   │   ├── admin_messages.html
│   │   │   ├── view_message.html
│   │   │   └── reply_message.html
│   │   ├── auth/               # 认证相关模板
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── forgot_password.html
│   │   │   ├── reset_password.html
│   │   │   ├── profile.html
│   │   │   └── edit_profile.html
│   │   └── errors/             # 错误页面模板
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/                  # 静态文件
│       ├── css/
│       ├── js/
│       │   ├── main.js
│       │   └── location-config.js
│       └── images/
├── app.py                       # 主应用文件
├── run.py                       # 启动脚本
├── config.py                    # 配置文件
├── requirements.txt             # 依赖包
├── README.md                    # 项目说明
├── LICENSE                      # 许可证
├── .gitignore                   # Git忽略文件
├── wsgi.py                      # WSGI入口
├── test_app.py                  # 测试文件
├── migrate_database.py          # 数据库迁移
├── migrate_projects.py          # 项目数据迁移
├── migrate_messages.py          # 消息数据迁移
├── start_server.py              # 服务器启动脚本
├── PORT_TROUBLESHOOTING.md      # 端口问题解决
└── PROJECT_STRUCTURE.md         # 项目结构说明
```

## 🏗️ 架构设计

### 1. **应用工厂模式**
- 使用 `create_app()` 函数创建应用实例
- 支持不同环境的配置
- 便于测试和扩展

### 2. **蓝图模块化**
- **main_bp**: 主要页面路由（首页、关于、项目、博客、联系）
- **admin_bp**: 管理后台路由（文章、项目、消息管理）
- **auth_bp**: 认证相关路由（登录、注册、个人资料）

### 3. **数据模型分离**
- **User**: 用户模型，支持认证和权限
- **Post**: 文章模型，支持博客功能
- **Project**: 项目模型，支持项目展示
- **Message**: 消息模型，支持联系表单

### 4. **工具函数模块**
- **filters.py**: 自定义模板过滤器
- 可扩展其他工具函数

## 🔧 技术栈

### 后端
- **Flask**: Web框架
- **SQLAlchemy**: ORM数据库操作
- **Flask-Login**: 用户认证
- **Werkzeug**: 密码哈希

### 前端
- **Bootstrap 5**: UI框架
- **Font Awesome**: 图标库
- **JavaScript**: 交互功能
- **HTML5/CSS3**: 页面结构

### 数据库
- **SQLite**: 开发环境
- **支持其他数据库**: 生产环境可配置

## 🚀 启动方式

### 开发环境
```bash
python3 run.py
```

### 生产环境
```bash
python3 wsgi.py
```

## 📝 主要功能

### 1. **前台功能**
- 首页展示
- 关于页面
- 项目展示（支持筛选和搜索）
- 项目详情页面
- 博客文章列表
- 文章详情页面
- 联系表单

### 2. **后台管理**
- 用户认证
- 文章管理（CRUD）
- 项目管理（CRUD）
- 消息管理
- 个人资料管理

### 3. **特色功能**
- 响应式设计
- 实时预览
- 文件上传
- 数据统计
- 搜索功能
- 分页显示

## 🔒 安全特性

- 密码哈希加密
- 表单验证
- CSRF保护
- 用户权限控制
- 输入过滤

## 📊 数据库设计

### 用户表 (User)
- id, username, email, password_hash, created_at

### 文章表 (Post)
- id, title, content, excerpt, slug, status, category, tags, featured_image, view_count, created_at, updated_at, author_id

### 项目表 (Project)
- id, title, description, short_description, image_url, github_url, live_url, demo_url, status, category, tags, technologies, features, challenges, lessons_learned, view_count, featured, created_at, updated_at

### 消息表 (Message)
- id, name, email, subject, message, status, ip_address, user_agent, created_at, read_at, replied_at

## 🎯 扩展建议

1. **邮件功能**: 集成邮件发送
2. **文件上传**: 支持图片上传
3. **缓存系统**: Redis缓存
4. **搜索功能**: 全文搜索
5. **API接口**: RESTful API
6. **监控系统**: 性能监控
7. **备份系统**: 数据备份

## 📚 开发规范

1. **代码风格**: 遵循PEP 8
2. **文档注释**: 函数和类必须有文档字符串
3. **错误处理**: 完善的异常处理
4. **日志记录**: 重要操作记录日志
5. **测试覆盖**: 单元测试和集成测试 