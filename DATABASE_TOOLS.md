# 🗄️ 数据库管理工具

## 📋 可用工具

### 1. **DB Browser for SQLite** (推荐)
- **安装**: `brew install --cask db-browser-for-sqlite`
- **特点**: 图形界面，功能强大，适合SQLite数据库
- **用途**: 可视化查看、编辑、管理数据库
- **数据库文件**: `personal_website.db`

### 2. **自定义数据库管理脚本**
- **文件**: `db_manager.py`
- **特点**: 命令行界面，集成到项目中
- **功能**: 完整的CRUD操作

## 🚀 使用方法

### 图形界面工具 (DB Browser)
```bash
# 打开应用
open "/Applications/DB Browser for SQLite.app"

# 或者从命令行打开数据库文件
open -a "DB Browser for SQLite" personal_website.db
```

### 命令行工具
```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行数据库管理工具
python db_manager.py
```

## 📊 数据库管理脚本功能

### 用户管理
- **查看用户**: 显示所有用户及其权限状态
- **创建用户**: 添加新用户，设置管理员权限
- **修改权限**: 更改用户的管理员状态
- **删除用户**: 删除指定用户

### 文章管理
- **查看文章**: 显示所有文章及其状态
- **创建文章**: 添加新文章，设置发布状态
- **删除文章**: 删除指定文章

### 项目管理
- **查看项目**: 显示所有项目及其完成状态
- **创建项目**: 添加新项目，设置技术栈和链接
- **删除项目**: 删除指定项目

### 消息管理
- **查看消息**: 显示所有联系消息及其回复状态
- **删除消息**: 删除指定消息

### 统计功能
- **数据库统计**: 显示各表的记录数量和状态统计

## 🔧 常用操作示例

### 1. 查看数据库状态
```bash
python db_manager.py
# 选择 13. 数据库统计
```

### 2. 创建管理员用户
```bash
python db_manager.py
# 选择 2. 创建新用户
# 输入用户信息，选择 y 设置为管理员
```

### 3. 修改用户权限
```bash
python db_manager.py
# 选择 3. 修改用户权限
# 输入用户ID，选择是否设置为管理员
```

### 4. 添加测试数据
```bash
python db_manager.py
# 选择 6. 创建新文章
# 选择 9. 创建新项目
```

## 📁 数据库文件位置

- **本地开发**: `personal_website.db` (项目根目录)
- **服务器**: `/home/website/personal_website.db`

## ⚠️ 注意事项

1. **备份重要数据**: 在进行删除操作前，建议备份数据库
2. **权限管理**: 只有管理员用户才能访问管理后台
3. **数据一致性**: 删除操作会永久删除数据，请谨慎操作
4. **服务器同步**: 本地修改不会自动同步到服务器，需要手动部署

## 🛠️ 高级操作

### 直接SQL查询 (使用DB Browser)
```sql
-- 查看所有管理员用户
SELECT * FROM user WHERE is_admin = 1;

-- 查看未发布的文章
SELECT * FROM post WHERE is_published = 0;

-- 查看未回复的消息
SELECT * FROM message WHERE is_replied = 0;

-- 统计各表记录数
SELECT 
    (SELECT COUNT(*) FROM user) as users,
    (SELECT COUNT(*) FROM post) as posts,
    (SELECT COUNT(*) FROM project) as projects,
    (SELECT COUNT(*) FROM message) as messages;
```

### 数据库备份
```bash
# 本地备份
cp personal_website.db personal_website_backup_$(date +%Y%m%d_%H%M%S).db

# 服务器备份
ssh root@47.112.96.87 "cd /home/website && cp personal_website.db personal_website_backup_$(date +%Y%m%d_%H%M%S).db"
```

## 🎯 推荐工作流程

1. **开发阶段**: 使用 `db_manager.py` 快速管理数据
2. **数据查看**: 使用 DB Browser 进行复杂查询和数据分析
3. **生产环境**: 通过管理后台进行日常数据管理
4. **定期备份**: 定期备份数据库文件

## 📞 技术支持

如果遇到问题：
1. 检查虚拟环境是否激活
2. 确认数据库文件存在
3. 查看错误日志
4. 联系技术支持 