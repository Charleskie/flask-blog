# 我的个人网站

一个基于Flask开发的现代化个人网站，包含博客、项目展示、联系表单等功能。

## ✨ 功能特性

- 🏠 **响应式首页** - 现代化的英雄区域和特色内容展示
- 👤 **关于页面** - 个人介绍、教育背景、工作经验等
- 💼 **项目展示** - 项目卡片展示，支持分类筛选
- 📝 **技术博客** - 文章列表、分页、搜索、分类
- 📧 **联系表单** - 完整的联系表单和社交媒体链接
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

# 或者直接运行
python app.py

# 或者使用Flask命令
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

访问 http://localhost:5000 查看网站

### 6. 测试应用

```bash
# 运行测试脚本
python test_app.py
```

## 📁 项目结构

```
my_web/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── wsgi.py               # WSGI入口文件
├── run.py                # 开发启动脚本
├── test_app.py           # 测试脚本
├── requirements.txt      # 项目依赖
├── README.md            # 项目说明
├── .gitignore           # Git忽略文件
├── templates/           # HTML模板
│   ├── base.html       # 基础模板
│   ├── index.html      # 首页
│   ├── about.html      # 关于页面
│   ├── projects.html   # 项目展示
│   ├── blog.html       # 博客页面
│   ├── contact.html    # 联系页面
│   ├── login.html      # 登录页面
│   ├── register.html   # 用户注册页面
│   ├── forgot_password.html # 忘记密码页面
│   ├── reset_password.html  # 重置密码页面
│   ├── profile.html    # 个人资料页面
│   ├── edit_profile.html # 编辑个人资料页面
│   ├── admin.html      # 管理后台
│   ├── 404.html        # 404错误页面
│   └── 500.html        # 500错误页面
└── static/             # 静态文件
    ├── css/
    │   └── style.css   # 自定义样式
    ├── js/
    │   └── main.js     # 主要JavaScript
    └── images/         # 图片资源
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
- GitHub: [your-username](https://github.com/Charleskie)
- 网站: [#](#)

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - CSS框架
- [Font Awesome](https://fontawesome.com/) - 图标库
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架

---

⭐ 如果这个项目对你有帮助，请给它一个星标！