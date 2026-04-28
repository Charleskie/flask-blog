# 个人网站系统

一个基于 Flask 的个人网站，当前代码已经覆盖公开内容展示、账户中心、站内互动、通知、消息会话和后台内容管理。

## 2.0.0

`v2.0.0` 是一次面向“站点统一性”和“可持续发布”的整理版本，重点不在单个页面堆功能，而在于把前台、账户中心、消息链路和后台编辑体验收成一套更一致的产品流。

### 本次版本重点
- **统一个人资料流**：后台和设置入口统一回到 `/profile` 与 `/profile/edit`，资料编辑支持除用户名外的全部内容。
- **统一消息中心**：新增统一入口 `/messages`，所有登录用户右上角都能看到消息中心入口；普通用户可直接与管理员对话，管理员进入后台会话列表。
- **统一编辑器体验**：关于页简化编辑 `/admin/about/simple` 已切换到和博客正文相同的 Toast UI 编辑器。
- **首页与友链页重构**：首页技术展示改成更轻量的平铺/滚动形式；友链页改成更简洁的链接展示。
- **生产部署链修正**：部署脚本改为以 `gunicorn + systemd + nginx` 为目标，HTTPS 申请和 Nginx 配置流程更稳定。

## 网站内容总览

### 公开前台
- **首页 `/`**：展示最新版本、常用技术、最近文章、热门文章、精选友链、站点统计。
- **博客 `/blog`**：支持分页、分类筛选、站内搜索、热门标签和热门文章。
- **文章详情 `/blog/post/<slug>`**：展示正文、相关文章，并接入点赞、收藏、评分、评论和评论回复。
- **关于 `/about`**：展示后台维护的关于内容。
- **关于 PDF `/about/pdf`**：将关于页内容导出为 PDF。
- **友链 `/links`**：展示活跃友链名称列表，并支持友链申请。
- **联系 `/contact`**：既是公开联系页，也是登录用户的会话中心；支持发起消息、查看管理员回复、继续跟进、删除个人侧会话。
- **统一消息中心 `/messages`**：根据登录身份自动跳到用户会话页或管理员消息页。
- **全站搜索 `/search`**：按关键词搜索已发布文章。

### 账户中心
- **登录 `/login`**、**注册 `/register`**、**忘记密码 `/forgot-password`**、**重置密码 `/reset-password/<token>`**。
- **个人资料 `/profile`**：展示用户资料、内容统计、公开状态和最近登录信息。
- **编辑资料 `/profile/edit`**：支持修改除用户名外的全部资料项，包括头像、邮箱、昵称、简介、网站、公司、职位、所在地、电话、资料公开状态、展示设置和密码。
- **设置首页 `/settings`**：作为账户相关入口聚合页。
- **隐私设置 `/settings/privacy`**：控制资料公开、邮箱显示、电话显示。
- **头像上传 `/settings/avatar`**：为资料页和编辑资料页提供头像上传接口。

### 通知与互动
- **通知中心 `/notifications`**：查看评论、回复、点赞、收藏、评分等通知。
- **互动 API `/api/...`**：
  点赞、收藏、评分、评论、评论回复、评论点赞、用户互动状态、富文本图片上传。
- **访问统计 API**：
  `/api/visitor-stats`、`/api/track-visit`。

### 管理后台
- **后台首页 `/admin`**：统计数据、最近文章、最近会话、快速入口。
- **文章管理**：新建、编辑、删除、状态切换、分类建议。
- **消息管理**：查看联系消息、管理员回复、删除回复、批量删除、状态更新、未读统计。
- **关于页管理**：维护关于内容区块和联系方式区块，支持简化编辑页 `/admin/about/simple`。
- **技能管理**：维护技能名称、图标、分类、熟练度和排序。
- **版本管理**：维护版本号、标题、描述和发布日期。
- **友链管理**：审核申请、手动新增、编辑、删除、推荐排序。

## 当前实现状态

- 当前主资料流是 `/profile` 和 `/profile/edit`。
- `/settings/profile` 仍保留，但 `GET` 会重定向到 `/profile`，主要用于兼容旧入口。
- 独立的 **安全设置页面已移除**；旧地址 `/settings/security` 会自动跳转回 `/settings`。
- 所有登录用户都可以从顶部入口进入 **消息中心**；普通用户进入 `/contact` 的对话视图，管理员进入 `/admin/messages`。
- 通知中心与消息中心已经拆分：站内通知继续走 `/notifications`，联系人会话统一走 `/messages` / `/contact`。
- 仓库中存在 Google / GitHub / 微信 OAuth 登录路由，但实际是否可用取决于 `.env` 中是否配置了对应凭证。
- 管理后台访问依赖数据库中存在 `is_admin=True` 的用户；代码里**没有**自动创建默认管理员账户的逻辑。

## 快速开始

### 环境要求
- Python 3.8+
- SQLite
- 现代浏览器

### 本地开发

```bash
# 1. 克隆项目
git clone <repository-url>
cd my_web

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库并启动开发服务
python run.py

# 或使用脚本启动
./start_dev.sh
```

默认访问地址：
- 前台：`http://localhost:8000`
- 后台：`http://localhost:8000/admin`

### 生产启动

```bash
./start_prod.sh
```

### 定时任务统一管理

项目内已经提供统一任务入口，不再要求把应用任务散落写在服务器 `crontab` 里。

```bash
# 查看全部已注册任务
python -m app.tasks.cli list

# 手动执行单个任务
python -m app.tasks.cli run project.log_cleanup

# 启动常驻调度器
python -m app.tasks.cli scheduler

# 输出 systemd service 示例
python -m app.tasks.cli export-systemd
```

当前已纳入注册表的任务来源：
- 仓库内原有的日志清理任务。
- 服务器 `crontab` 中的 `/opt/stock-collector` 采集、预测、飞书报告任务。
- 服务器 `crontab` 中的 `certbot renew` 任务。

说明：
- 调度器设计为**独立进程**，不要直接嵌进 Gunicorn worker 内，否则会重复执行。
- 股票采集相关任务默认读取 `STOCK_COLLECTOR_ROOT` 和 `STOCK_COLLECTOR_PYTHON`；路径不存在时任务会显示为 `disabled`。
- 证书续期已经被录入注册表，但服务器如果还保留 `certbot-renew.timer` 或重复 `crontab` 项，需要切换时一并清理，避免重复执行。

### 部署脚本

```bash
./deploy_sample.sh
```

说明：
- `deploy_sample.sh` 是脱敏后的示例脚本，适合作为指导模板。
- 实际生产部署建议使用你自己的正式脚本副本，并结合 `gunicorn + systemd + nginx`。
- 部署脚本会自动生成 `APP_VERSION`：优先取当前 `git tag`，没有 tag 时回退到 `git describe` / commit 标识。

## 核心路由

### 前台页面
- `/`
- `/about`
- `/about/pdf`
- `/links`
- `/blog`
- `/blog/post/<slug>`
- `/contact`
- `/messages`
- `/search`

### 账户与设置
- `/login`
- `/register`
- `/forgot-password`
- `/reset-password/<token>`
- `/profile`
- `/profile/edit`
- `/settings`
- `/settings/privacy`

### 通知
- `/notifications`
- `/notifications/<int:notification_id>`

### 管理后台
- `/admin`
- `/admin/posts`
- `/admin/messages`
- `/admin/about`
- `/admin/about/simple`
- `/admin/skills`
- `/admin/links`
- `/admin/versions`

## 主要功能模块

### 内容系统
- 文章支持 `HTML` 和 `Markdown` 两种正文格式。
- 文章包含摘要、分类、标签、特色图片、浏览量、点赞数、收藏数、评论数和平均评分。
- 首页和博客页都围绕已发布文章组织内容。

### 联系与会话系统
- 访客可通过联系页提交消息。
- 登录用户可通过右上角消息中心进入自己的会话页。
- 管理员可在后台继续回复，形成消息对话。
- 登录用户可在前台查看自己的对话记录、接收管理员回复、继续跟进消息。
- 会话支持用户侧和管理员侧单独删除，双方都删除后才彻底清理。

### 评论与互动系统
- 登录用户可点赞、收藏、评分、评论文章。
- 评论支持回复和二级回复。
- 评论支持单独点赞。
- 对内容作者会自动生成通知。

### 通知系统
- 支持评论、回复、点赞、收藏、评分等通知类型。
- 支持筛选、标记已读、全部已读、删除通知。

### 账户中心
- 资料页提供统计信息、公开状态、最近登录时间等概览。
- 编辑页整合头像、资料、公开范围和密码修改。
- 隐私页控制资料是否公开，以及邮箱/电话是否对外展示。

### 编辑器与后台体验
- 博客正文编辑使用 Toast UI Editor。
- 关于页简化编辑页已切换到与博客一致的编辑器。
- 后台消息页与前台用户会话页使用统一的双栏对话式布局。

## 项目结构

```text
my_web/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   └── oauth.py
│   ├── models/
│   │   ├── about.py
│   │   ├── interaction.py
│   │   ├── link.py
│   │   ├── message.py
│   │   ├── message_reply.py
│   │   ├── notification.py
│   │   ├── post.py
│   │   ├── skill.py
│   │   ├── user.py
│   │   ├── version.py
│   │   └── visitor_stats.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── interaction.py
│   │   ├── main.py
│   │   ├── notifications.py
│   │   ├── settings.py
│   │   └── version.py
│   ├── templates/
│   │   ├── admin/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── errors/
│   │   ├── frontend/
│   │   ├── notifications/
│   │   └── settings/
│   └── utils/
│       ├── email_sender.py
│       ├── filters.py
│       ├── logger.py
│       ├── pdf_generator.py
│       └── post_content.py
├── app.py
├── run.py
├── config.py
├── db_manager.py
├── db_tools.py
├── deploy_kim.sh
├── deploy_sample.sh
├── restart_website.sh
├── setup_log_cleanup.sh
├── start_dev.sh
├── start_prod.sh
├── EMAIL_SETUP_GUIDE.md
├── MAIL_SETUP.md
└── SCHEMA_CHANGES.sql
```

## 数据模型

### 核心模型
- **User**：登录账号、个人资料、隐私设置、OAuth 标识、密码重置令牌。
- **Post**：文章内容、格式、标签、统计数据。
- **Message**：联系消息和会话主表。
- **MessageReply**：管理员或用户对消息的回复记录。
- **Notification**：站内通知。
- **Comment / CommentReply / CommentLike / UserInteraction**：文章互动体系。
- **AboutContent / AboutContact**：关于页内容和联系方式。
- **Skill**：技能卡片内容。
- **Version**：版本更新记录。
- **Link**：友链和友链申请。
- **VisitorStats**：访问量统计。

### 关系概览
- 用户与文章：一对多
- 用户与评论：一对多
- 文章与评论：一对多
- 评论与回复：一对多
- 消息与回复：一对多
- 用户与通知：一对多

## 配置说明

### 基础环境变量

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///personal_website.db
```

### 邮件配置

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### OAuth 配置（可选）

```bash
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
WECHAT_APP_ID=
WECHAT_APP_SECRET=
```

### 文件上传

```bash
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=app/static/uploads
```

### 生产部署相关

```bash
FORCE_HTTPS=false
SERVER_NAME=example.com
APP_VERSION=v2.0.0
```

## 维护脚本

### 数据库与数据

```bash
python db_manager.py
python db_tools.py
```

### 服务与日志

```bash
./restart_website.sh
./setup_log_cleanup.sh
python cleanup_logs.py
tail -f logs/app.log
```

## 文档与辅助文件

- [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)：邮件服务配置说明
- [MAIL_SETUP.md](MAIL_SETUP.md)：邮件相关补充说明
- [SCHEMA_CHANGES.sql](SCHEMA_CHANGES.sql)：数据库结构变更记录
- [app/templates/README.md](app/templates/README.md)：模板结构说明

## 开发注意事项

- `interaction` 蓝图注册在 `/api` 前缀下，因此互动接口实际路径形如 `/api/comment`、`/api/like`。
- 应用启动时会自动执行部分数据库兼容修复：
  为文章补齐 `content_format`，为消息补齐删除/已读字段，为评论回复补齐二级回复字段。
- 当前工作区里存在一些未提交的本地改动；如果要发布 `v2.0.0`，建议先确认本次版本应包含的文件范围，再统一提交和打 tag。
- 模板中的静态资源现在统一通过 `APP_VERSION` 做缓存失效；发版时如果在 tag 上部署，会自动使用 tag 名作为版本参数。
- 如果启用了 `FORCE_HTTPS`，应用会在生产环境中接入 HTTPS 重定向。

## 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE)。
