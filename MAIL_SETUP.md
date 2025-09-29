# 邮件配置说明

## 问题说明
如果您在使用忘记密码功能时没有收到邮件，这是因为系统还没有配置邮件服务器。

## 配置步骤

### 1. 选择邮箱服务商
推荐使用以下邮箱服务商：
- Gmail（推荐）
- QQ邮箱
- 163邮箱
- Outlook/Hotmail

### 2. Gmail 配置（推荐）

#### 2.1 启用两步验证
1. 登录 Gmail 账户
2. 进入 [Google 账户安全设置](https://myaccount.google.com/security)
3. 启用"两步验证"

#### 2.2 生成应用专用密码
1. 在安全设置中找到"应用专用密码"
2. 选择"邮件"和"其他（自定义名称）"
3. 输入应用名称（如：个人网站）
4. 生成16位密码并保存

#### 2.3 配置环境变量
创建 `.env` 文件或设置环境变量：
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=*****
MAIL_FROM=your@gmail.com
MAIL_DEFAULT_SENDER=your@gmail.com
```

### 3. QQ邮箱配置

#### 3.1 开启SMTP服务
1. 登录QQ邮箱
2. 进入"设置" > "账户"
3. 开启"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 获取授权码

#### 3.2 配置环境变量
```bash
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-authorization-code
MAIL_FROM=your-email@qq.com
MAIL_DEFAULT_SENDER=your-email@qq.com
```

### 4. 163邮箱配置

#### 4.1 开启SMTP服务
1. 登录163邮箱
2. 进入"设置" > "POP3/SMTP/IMAP"
3. 开启"SMTP服务"
4. 获取授权码

#### 4.2 配置环境变量
```bash
MAIL_SERVER=smtp.163.com
MAIL_PORT=25
MAIL_USE_TLS=False
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-authorization-code
MAIL_FROM=your-email@163.com
MAIL_DEFAULT_SENDER=your-email@163.com
```

## 测试邮件发送

### 方法1：通过忘记密码功能测试
1. 访问忘记密码页面
2. 输入已注册的邮箱地址
3. 点击"发送重置链接"
4. 检查邮箱（包括垃圾邮件文件夹）

### 方法2：通过控制台测试
```bash
cd /Users/shengwang/my_web
python3 -c "
from app import create_app
from app.models.user import User
from app.routes.auth import send_reset_email

app = create_app()
with app.app_context():
    user = User.query.first()
    if user:
        token = user.generate_reset_token()
        result = send_reset_email(user, token)
        print(f'邮件发送结果: {result}')
    else:
        print('没有找到用户')
"
```

## 常见问题

### Q1: 邮件发送失败
**解决方案：**
1. 检查邮箱用户名和密码是否正确
2. 确认已开启SMTP服务
3. 检查网络连接
4. 查看应用日志获取详细错误信息

### Q2: 邮件进入垃圾箱
**解决方案：**
1. 将发送邮箱添加到联系人
2. 在邮箱设置中将发送邮箱设为白名单
3. 检查邮件内容是否包含敏感词汇

### Q3: Gmail提示"不允许使用安全性较低的应用"
**解决方案：**
1. 使用应用专用密码而不是账户密码
2. 确保已启用两步验证
3. 在Google账户中允许"安全性较低的应用"

### Q4: 163邮箱连接超时
**解决方案：**
1. 尝试使用端口465和SSL
2. 检查防火墙设置
3. 联系网络管理员

## 安全建议

1. **使用应用专用密码**：不要使用账户主密码
2. **定期更换密码**：建议每3-6个月更换一次
3. **限制发送频率**：避免频繁发送邮件被标记为垃圾邮件
4. **监控日志**：定期检查邮件发送日志

## 生产环境建议

1. **使用专业邮件服务**：如SendGrid、Mailgun、Amazon SES
2. **配置邮件队列**：使用Celery等异步任务队列
3. **设置邮件模板**：使用Jinja2模板引擎
4. **监控邮件送达率**：跟踪邮件发送成功率

## 联系支持

如果遇到问题，请：
1. 查看应用日志文件
2. 检查环境变量配置
3. 确认邮箱服务商设置
4. 联系技术支持
