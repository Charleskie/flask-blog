# 个人网站

一个基于Flask开发的现代化个人网站，包含博客、项目展示、联系表单等功能。

## ✨ 功能特性

- 📝 **博客系统** - 文章发布、编辑、管理
- 🚀 **项目展示** - 项目介绍、技术栈展示
- 📧 **联系表单** - 访客留言、消息管理
- 👤 **用户管理** - 用户注册、登录、权限控制
- 📱 **移动端适配** - 完全响应式设计
- 🎨 **现代化UI** - 基于Bootstrap 5的美观界面

## 🚀 快速部署

### 一键部署到服务器

```bash
# 部署到默认服务器
./deploy.sh

# 或指定服务器
./deploy.sh 你的服务器IP root
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python simple_migrate.py

# 启动开发服务器
python run.py
```

访问 http://localhost:5001 查看网站

## 📋 默认管理员账户

- 用户名：`admin`
- 密码：`admin123`
- 访问：http://localhost:5001/admin

## 📁 项目结构

```
my_web/
├── app/                    # 主应用代码
│   ├── __init__.py        # 应用工厂
│   ├── models/            # 数据模型
│   ├── routes/            # 路由
│   ├── templates/         # 模板文件
│   ├── static/            # 静态文件
│   └── utils/             # 工具函数
├── app.py                 # 应用入口
├── run.py                 # 开发服务器启动脚本
├── simple_migrate.py      # 数据库初始化脚本
├── requirements.txt       # Python依赖
├── deploy.sh              # 一键部署脚本
└── README.md              # 项目说明
```

## 🔧 技术栈

- **后端**: Flask 1.1.4 + SQLAlchemy 2.5.1
- **数据库**: SQLite
- **前端**: Bootstrap 5.3.0 + Font Awesome 6.4.0
- **认证**: Flask-Login 0.5.0
- **部署**: Gunicorn + Nginx

## 🛠️ 常用命令

### 维护脚本（推荐使用）

项目提供了三个实用的维护脚本：

#### 1. 网站状态检查
```bash
# 检查网站运行状态
./check_website.sh

# 检查内容包括：
# - 服务状态（website、nginx）
# - 端口监听（80、8000）
# - 本地和外部访问测试
# - 系统资源使用情况
# - 项目文件完整性
# - 防火墙配置
```

#### 2. 网站重启
```bash
# 重启网站服务
./restart_website.sh

# 重启过程包括：
# - 安全停止所有服务
# - 清理端口占用
# - 重新加载配置
# - 启动服务并验证
# - 测试访问功能
```

#### 3. 网站备份
```bash
# 备份网站数据
./backup_website.sh [备份目录]

# 备份内容包括：
# - 数据库文件
# - 项目源代码
# - 配置文件（Nginx、systemd）
# - 系统信息
# - 自动清理7天前的旧备份
```

### 手动命令

```bash
# 查看服务状态
sudo systemctl status website

# 重启服务
sudo systemctl restart website

# 查看日志
sudo journalctl -u website -f

# 重启Nginx
sudo systemctl restart nginx
```

### 故障排查

#### 网站无法访问
```bash
# 1. 检查服务状态
sudo systemctl status website nginx

# 2. 检查端口监听
netstat -tlnp | grep -E ':(80|8000)'

# 3. 检查本地访问
curl -v http://localhost:8000

# 4. 检查防火墙
sudo firewall-cmd --list-all
```

#### 服务启动失败
```bash
# 1. 查看详细错误
sudo journalctl -u website --no-pager -n 50

# 2. 检查配置文件
python -m py_compile /home/website/app.py

# 3. 手动启动测试
cd /home/website
source venv/bin/activate
python app.py
```

详细维护指南请参考 [MAINTENANCE.md](MAINTENANCE.md) 文档。

## 📞 获取帮助

如果遇到问题，请检查：
1. 服务器防火墙设置
2. 阿里云安全组配置
3. 服务日志文件

---

⭐ 如果这个项目对你有帮助，请给一个星标！