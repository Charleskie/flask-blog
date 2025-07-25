# 我的个人网站

一个基于Flask开发的现代化个人网站，包含博客、项目展示、联系表单等功能。

## ✨ 功能特性

- 🏠 **响应式首页** - 现代化的英雄区域和特色内容展示
- 👤 **关于页面** - 个人介绍、教育背景、工作经验等
- 💼 **项目展示** - 完整的项目管理功能，包括技术栈、功能特性、挑战经验等
- 📝 **技术博客** - 文章发布、编辑、分类、标签、搜索功能，支持Markdown格式
- 📧 **联系表单** - 完整的联系表单和消息管理系统
- 🔐 **用户认证系统** - 完整的注册、登录、密码重置功能
- 👤 **个人资料管理** - 用户资料查看和编辑
- 🔒 **账户安全** - 密码强度检测、安全设置
- 📱 **移动端适配** - 完全响应式设计
- 🎨 **现代化UI** - 基于Bootstrap 5的美观界面

## 🚀 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLAlchemy + SQLite
- **前端**: Bootstrap 5.3.0 + Font Awesome 6.4.0
- **认证**: Flask-Login
- **表单**: Flask-WTF
- **部署**: Gunicorn

## 📦 安装和运行

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd my_web
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python app.py
```

### 5. 运行应用

```bash
# 开发环境（推荐）
python run.py

# 智能端口选择（推荐）
python start_server.py

# 或者直接运行
python app.py

# 或者使用Flask命令
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

访问 http://localhost:5001 查看网站

**注意**：如果端口5000被占用（macOS上通常是AirPlay Receiver），应用会自动使用端口5001。

### 6. 测试应用

```bash
# 运行测试脚本
python test_app.py
```

## 📁 项目结构

```
my_web/
├── app.py                 # 主应用文件
├── run.py                # 开发启动脚本（端口5001）
├── start_server.py       # 智能端口选择启动脚本
├── test_app.py           # 测试脚本
├── migrate_database.py   # 数据库迁移脚本
├── migrate_projects.py   # 项目数据库迁移脚本
├── migrate_messages.py   # 消息数据库迁移脚本
├── requirements.txt      # 项目依赖
├── README.md            # 项目说明
├── PORT_TROUBLESHOOTING.md # 端口问题解决指南
├── .gitignore           # Git忽略文件
├── templates/           # HTML模板
│   ├── base.html       # 基础模板
│   ├── index.html      # 首页
│   ├── about.html      # 关于页面
│   ├── projects.html   # 项目展示页面
│   ├── blog.html       # 博客列表页面
│   ├── contact.html    # 联系页面
│   ├── login.html      # 登录页面
│   ├── register.html   # 用户注册页面
│   ├── forgot_password.html # 忘记密码页面
│   ├── reset_password.html  # 重置密码页面
│   ├── profile.html    # 个人资料页面
│   ├── edit_profile.html # 编辑个人资料页面
│   ├── admin.html      # 管理后台
│   ├── admin_posts.html # 文章管理页面
│   ├── new_post.html   # 新建文章页面
│   ├── admin_projects.html # 项目管理页面
│   ├── new_project.html # 新建项目页面
│   ├── admin_messages.html # 消息管理页面
│   ├── view_message.html # 查看消息页面
│   ├── reply_message.html # 回复消息页面
│   ├── 404.html        # 404错误页面
│   └── 500.html        # 500错误页面
└── static/             # 静态文件
    ├── css/
    │   └── style.css   # 自定义样式
    ├── js/
    │   └── main.js     # 主要JavaScript
    ├── images/         # 图片资源
    │   ├── favicon.svg # 网站图标
    │   ├── icon-16x16.svg # 16x16图标
    │   ├── icon-32x32.svg # 32x32图标
    │   └── icon-192x192.svg # 192x192图标
    ├── manifest.json   # PWA清单文件
    └── browserconfig.xml # Windows磁贴配置
```

## 🔧 配置说明

### 环境变量

创建 `.env` 文件来配置环境变量：

```env
# 基础配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 数据库配置
DATABASE_URL=sqlite:///personal_website.db

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 数据库配置

项目使用SQLite作为默认数据库，首次运行时会自动创建数据库文件。

## 🎨 自定义主题

### 修改颜色主题

编辑 `static/css/style.css` 文件中的CSS变量：

```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --info-color: #17a2b8;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
}
```

### 添加自定义样式

在 `static/css/style.css` 中添加你的自定义样式。

### 网站图标

项目包含完整的网站图标系统：

#### 图标文件
- `static/images/favicon.svg` - 主要SVG图标
- `static/images/icon-16x16.svg` - 小尺寸图标
- `static/images/icon-32x32.svg` - 标准尺寸图标
- `static/images/icon-192x192.svg` - 高分辨率图标

#### 支持的功能
- 浏览器标签页图标
- 书签图标
- 移动设备主屏幕图标
- PWA应用图标
- Windows磁贴图标
- 社交媒体分享预览

#### 预览图标
打开 `icon_preview.html` 文件可以在浏览器中预览所有图标。

## 🔐 用户认证系统

### 用户注册

1. 访问 `/register` 页面
2. 填写用户名、邮箱、密码等信息
3. 同意服务条款和隐私政策
4. 点击注册按钮完成注册

**注册要求：**
- 用户名：3-20位，只能包含字母、数字和下划线
- 邮箱：有效的邮箱地址
- 密码：至少6位，建议包含字母、数字和特殊字符

### 用户登录

1. 访问 `/login` 页面
2. 输入用户名和密码
3. 可选择"记住我"功能
4. 点击登录按钮

### 密码管理

- **忘记密码**：访问 `/forgot-password` 页面，输入邮箱获取重置链接
- **修改密码**：登录后在个人资料页面修改密码
- **密码强度**：实时显示密码强度指示器

### 个人资料管理

- **查看资料**：访问 `/profile` 页面查看个人信息
- **编辑资料**：访问 `/edit_profile` 页面修改邮箱等信息
- **安全设置**：配置邮件通知、登录通知等安全选项

## 📝 博客文章系统

### 文章管理

1. **新建文章**：访问 `/admin/posts/new` 页面
   - 支持Markdown格式编写
   - 自动生成文章摘要
   - 设置分类和标签
   - 文章预览功能

2. **文章编辑**：访问 `/admin/posts` 管理文章列表
   - 编辑文章内容和设置
   - 更改发布状态
   - 删除文章

3. **文章功能**
   - 文章分类和标签管理
   - 特色图片设置
   - 浏览次数统计
   - 相关文章推荐

### 文章展示

- **文章列表**：支持分页、分类筛选、搜索
- **文章详情**：完整的文章内容展示
- **响应式设计**：适配各种设备

## 💼 项目管理系统

### 项目管理

1. **新建项目**：访问 `/admin/projects/new` 页面
   - 项目基本信息（标题、描述）
   - 技术栈记录
   - 功能特性列表
   - 开发挑战和经验总结
   - 项目链接管理（GitHub、演示、视频）

2. **项目编辑**：访问 `/admin/projects` 管理项目列表
   - 编辑项目信息
   - 更改项目状态
   - 设置推荐项目
   - 删除项目

### 项目展示

- **项目列表**：支持分类筛选、搜索、推荐项目优先显示
- **项目详情**：完整展示项目信息和技术栈
- **技术标签**：展示项目使用的技术
- **浏览次数统计**

## 📧 消息管理系统

### 消息接收

1. **联系表单**：访问者通过联系页面发送消息
   - 表单验证（姓名、邮箱、主题、内容）
   - 邮箱格式验证
   - 自动记录IP地址和用户代理信息

2. **消息存储**：所有消息自动保存到数据库
   - 消息状态管理（未读、已读、已回复、已归档）
   - 时间戳记录（发送时间、阅读时间、回复时间）

### 消息管理

1. **消息列表**：访问 `/admin/messages` 页面
   - 消息状态筛选（未读、已读、已回复、已归档）
   - 分页显示
   - 快速操作（查看、回复、删除、状态更改）

2. **消息详情**：查看完整消息内容
   - 发送者信息（姓名、邮箱、IP地址）
   - 时间信息（发送、阅读、回复时间）
   - 消息内容展示
   - 快速操作按钮

3. **消息回复**：回复访客消息
   - 回复内容编辑
   - 快速回复模板
   - 原消息对照显示
   - 自动标记为已回复

### 消息功能

- **状态管理**：未读、已读、已回复、已归档
- **筛选搜索**：按状态筛选消息
- **批量操作**：快速更改消息状态
- **统计信息**：未读消息数量、总消息数
- **安全记录**：IP地址、用户代理信息

## 📝 内容管理

### 添加项目

1. 登录管理后台
2. 点击"添加项目"
3. 填写项目信息（标题、描述、图片URL、GitHub链接等）

### 发布博客

1. 登录管理后台
2. 点击"新建文章"
3. 编写文章内容
4. 设置分类和标签

## 🚀 部署指南

### 使用Gunicorn部署

```bash
# 安装Gunicorn
pip install gunicorn

# 运行应用
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### 使用Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

构建和运行：

```bash
docker build -t my-website .
docker run -p 5000:5000 my-website
```

### 部署到云平台

#### Heroku

1. 创建 `Procfile`：
```
web: gunicorn wsgi:app
```

2. 部署：
```bash
heroku create your-app-name
git push heroku main
```

#### Vercel

1. 创建 `vercel.json`：
```json
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ]
}
```

## 🔒 安全注意事项

1. **生产环境配置**：
   - 设置强密码的 `SECRET_KEY`
   - 启用 `SESSION_COOKIE_SECURE`
   - 配置HTTPS

2. **数据库安全**：
   - 定期备份数据库
   - 使用强密码
   - 限制数据库访问

3. **文件上传**：
   - 验证文件类型
   - 限制文件大小
   - 存储到安全位置

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 邮箱: wdws851421092@gmail.com
- GitHub: [Charleskie](https://github.com/Charleskie)
- 网站: [-](-)

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - CSS框架
- [Font Awesome](https://fontawesome.com/) - 图标库
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架

---

⭐ 如果这个项目对你有帮助，请给它一个星标！