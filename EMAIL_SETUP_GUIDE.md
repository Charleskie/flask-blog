# 📧 邮件配置指导

## 问题描述
当前系统显示警告：`邮件配置不完整，无法发送回复邮件`

## 解决方案

### 1. 创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
touch .env
```

### 2. 配置邮件设置

在 `.env` 文件中添加以下配置：

#### Gmail 配置（推荐）
```bash
# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=wdws851421092@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_FROM=wdws851421092@gmail.com
MAIL_DEFAULT_SENDER=wdws851421092@gmail.com
```

#### 其他邮箱服务商

**QQ邮箱：**
```bash
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-authorization-code
```

**163邮箱：**
```bash
MAIL_SERVER=smtp.163.com
MAIL_PORT=25
MAIL_USE_TLS=False
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-authorization-code
```

**Outlook/Hotmail：**
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### 3. Gmail 应用密码设置

如果使用 Gmail，需要设置应用专用密码：

1. **登录 Google 账户**
2. **进入安全性设置**
   - 访问：https://myaccount.google.com/security
3. **启用两步验证**（如果未启用）
4. **生成应用专用密码**
   - 点击"应用专用密码"
   - 选择"邮件"
   - 生成16位密码
5. **使用应用密码**
   - 将生成的密码作为 `MAIL_PASSWORD` 的值

### 4. 验证配置

运行配置检查脚本：

```bash
python3 check_email_config.py
```

### 5. 测试邮件发送

配置完成后，系统会自动：
- 发送回复邮件给用户
- 记录邮件发送状态
- 在消息详情中显示发送状态

## 配置示例

完整的 `.env` 文件示例：

```bash
# 应用配置
SECRET_KEY=your-secret-key-here

# HTTPS 配置
SERVER_NAME=www.shiheng.info
FORCE_HTTPS=true
FORCE_WWW=true
SESSION_COOKIE_SECURE=False

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=wdws851421092@gmail.com
MAIL_PASSWORD=your-16-digit-app-password
MAIL_FROM=wdws851421092@gmail.com
MAIL_DEFAULT_SENDER=wdws851421092@gmail.com
```

## 注意事项

1. **安全性**：不要将 `.env` 文件提交到版本控制系统
2. **密码**：Gmail 必须使用应用专用密码，不能使用账户密码
3. **权限**：确保邮箱账户允许"不够安全的应用"访问（如果适用）
4. **测试**：配置完成后建议先发送测试邮件验证

## 故障排除

### 常见错误

1. **认证失败**
   - 检查用户名和密码是否正确
   - Gmail 用户确保使用应用专用密码

2. **连接超时**
   - 检查网络连接
   - 确认 SMTP 服务器地址和端口

3. **TLS 错误**
   - 确认 `MAIL_USE_TLS` 设置正确
   - 某些邮箱服务商需要特定的 TLS 设置

### 获取帮助

如果遇到问题，可以：
1. 运行 `python3 check_email_config.py` 进行诊断
2. 查看应用日志获取详细错误信息
3. 参考邮箱服务商的官方文档
