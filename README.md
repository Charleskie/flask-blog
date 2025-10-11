# 个人网站系统

一个功能完整的现代化个人网站，基于Flask开发，集成了博客、项目展示、联系表单、用户管理、PDF导出等多项功能。

## ✨ 核心功能

### 📝 内容管理
- **博客系统** - 文章发布、编辑、分类、标签管理
- **项目展示** - 项目介绍、技术栈展示、分类筛选
- **关于页面** - 个人简介、技能展示、联系方式
- **版本记录** - 网站更新日志、功能发布记录

### 👥 用户系统
- **用户注册/登录** - 完整的用户认证系统
- **权限管理** - 管理员、普通用户权限控制
- **个人资料** - 用户信息管理、头像上传
- **消息系统** - 站内消息、通知提醒

### 💬 互动功能
- **联系表单** - 访客留言、消息管理
- **评论系统** - 文章评论、回复功能
- **点赞收藏** - 内容互动、用户反馈
- **搜索功能** - 全站内容搜索

### 📄 特色功能
- **PDF导出** - 关于页面内容导出为PDF格式
- **富文本编辑** - 支持Markdown和富文本编辑
- **响应式设计** - 完美适配桌面和移动设备
- **SEO优化** - 搜索引擎友好的URL结构

## 🚀 快速开始

### 环境要求
- Python 3.8+
- SQLite 数据库
- 现代浏览器

### 本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd my_web

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python run.py

# 4. 启动开发服务器
./start_dev.sh
# 或
python run.py
```

访问 http://localhost:8000 查看网站

### 生产部署

```bash
# 一键部署到服务器
./deploy.sh [服务器IP] [用户名] [是否启用HTTPS] [SSH密码]

# 示例
./deploy.sh 47.112.96.87 root true your_password
```

## 📋 默认账户

### 管理员账户
- **用户名**: `admin`
- **密码**: `admin123`
- **访问地址**: http://localhost:8000/admin

### 功能权限
- 内容管理（文章、项目、关于页面）
- 用户管理
- 消息管理
- 系统设置

## 🏗️ 项目架构

### 目录结构
```
my_web/
├── app/                          # 主应用代码
│   ├── __init__.py              # 应用工厂
│   ├── models/                  # 数据模型
│   │   ├── user.py             # 用户模型
│   │   ├── post.py             # 文章模型
│   │   ├── project.py          # 项目模型
│   │   ├── message.py          # 消息模型
│   │   ├── about.py            # 关于页面模型
│   │   ├── skill.py            # 技能模型
│   │   ├── version.py          # 版本记录模型
│   │   ├── interaction.py      # 互动模型
│   │   └── notification.py     # 通知模型
│   ├── routes/                  # 路由控制器
│   │   ├── main.py             # 前台路由
│   │   ├── admin.py            # 管理后台路由
│   │   ├── auth.py             # 认证路由
│   │   ├── settings.py         # 设置路由
│   │   └── notifications.py    # 通知路由
│   ├── templates/               # 模板文件
│   │   ├── frontend/           # 前台模板
│   │   ├── admin/              # 管理后台模板
│   │   ├── auth/               # 认证模板
│   │   └── errors/             # 错误页面模板
│   ├── static/                  # 静态资源
│   │   ├── css/                # 样式文件
│   │   ├── js/                 # JavaScript文件
│   │   ├── images/             # 图片资源
│   │   └── uploads/            # 上传文件
│   └── utils/                   # 工具函数
│       ├── pdf_generator.py    # PDF生成器
│       ├── email_sender.py     # 邮件发送
│       ├── filters.py          # 模板过滤器
│       └── logger.py           # 日志管理
├── config.py                    # 配置文件
├── run.py                       # 开发服务器启动
├── app.py                       # 生产环境启动
├── requirements.txt             # Python依赖
├── deploy.sh                    # 一键部署脚本
└── README.md                    # 项目说明
```

### 技术栈

#### 后端技术
- **Flask 3.1.1** - Web框架
- **SQLAlchemy 3.1.1** - ORM数据库操作
- **Flask-Login 0.6.3** - 用户认证
- **ReportLab 4.0.9** - PDF生成
- **Pillow 10.4.0** - 图像处理
- **Markdown 3.5.1** - 文本处理

#### 前端技术
- **Bootstrap 5** - UI框架
- **Font Awesome 6** - 图标库
- **jQuery** - JavaScript库
- **TipTap** - 富文本编辑器

#### 部署技术
- **Gunicorn** - WSGI服务器
- **Nginx** - 反向代理
- **SQLite** - 数据库
- **Systemd** - 服务管理

## 🛠️ 管理工具

### 数据库管理
```bash
# 数据库管理工具
python db_manager.py

# 功能包括：
# - 用户管理
# - 内容管理
# - 数据库备份/恢复
# - 表结构管理
```

### 维护脚本
```bash
# 网站状态检查
./check_website.sh

# 网站重启
./restart_website.sh

# 网站备份
./backup_website.sh [备份目录]
```

### 日志管理
```bash
# 查看应用日志
tail -f logs/app.log

# 查看服务器日志
sudo journalctl -u website -f

# 清理日志
./setup_log_cleanup.sh
```

## 📊 数据模型

### 核心模型
- **User** - 用户信息、权限管理
- **Post** - 文章内容、分类标签
- **Project** - 项目展示、技术栈
- **Message** - 联系消息、回复
- **AboutContent** - 关于页面内容
- **Skill** - 技能展示、熟练度
- **Version** - 版本记录、更新日志
- **Notification** - 系统通知

### 关系设计
- 用户与文章：一对多
- 用户与项目：一对多
- 文章与评论：一对多
- 消息与回复：一对多

## 🔧 配置说明

### 环境变量
```bash
# 基础配置
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///personal_website.db

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# 文件上传
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=app/static/uploads
```

### 功能配置
- **PDF导出** - 支持中文字体、自定义样式
- **邮件通知** - 支持SMTP邮件发送
- **文件上传** - 支持图片、文档上传
- **日志记录** - 完整的操作日志

## 🚀 部署指南

### 开发环境
```bash
# 启动开发服务器
./start_dev.sh

# 访问地址
http://localhost:8000
```

### 生产环境
```bash
# 一键部署
./deploy.sh

# 手动部署
./start_prod.sh
```

### 服务管理
```bash
# 查看服务状态
sudo systemctl status website

# 重启服务
sudo systemctl restart website

# 查看日志
sudo journalctl -u website -f
```

## 📱 功能演示

### 前台功能
- **首页** - 最新文章、推荐项目
- **博客** - 文章列表、分类筛选、搜索
- **项目** - 项目展示、技术栈、详情页
- **关于** - 个人简介、技能展示、PDF下载
- **联系** - 留言表单、消息管理

### 管理后台
- **仪表板** - 数据统计、快速操作
- **内容管理** - 文章、项目、关于页面
- **用户管理** - 用户列表、权限设置
- **消息管理** - 联系消息、回复处理
- **系统设置** - 网站配置、邮件设置

## 🔍 故障排查

### 常见问题
1. **服务无法启动** - 检查端口占用、依赖安装
2. **数据库错误** - 检查数据库文件权限
3. **邮件发送失败** - 检查SMTP配置
4. **文件上传失败** - 检查上传目录权限

### 日志分析
```bash
# 应用日志
tail -f logs/app.log

# 错误日志
grep "ERROR" logs/app.log

# 访问日志
sudo tail -f /var/log/nginx/access.log
```

## 📄 相关文档

- [PDF功能说明](PDF_FEATURE_README.md) - PDF导出功能详细说明
- [邮件设置指南](EMAIL_SETUP_GUIDE.md) - 邮件服务配置
- [部署故障排查](DEPLOYMENT_TROUBLESHOOTING.md) - 部署问题解决

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- **项目地址**: [GitHub Repository]
- **问题反馈**: [Issues]
- **邮箱**: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给一个星标！