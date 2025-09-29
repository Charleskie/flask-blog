import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

def send_reply_email(original_message, reply_content, reply_record=None):
    """
    发送回复邮件给用户
    
    Args:
        original_message: 原始消息对象
        reply_content: 回复内容
        reply_record: 回复记录对象（可选）
    
    Returns:
        bool: 发送是否成功
    """
    try:
        # 检查邮件配置
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_from = current_app.config.get('MAIL_FROM', 'noreply@example.com')

        print(current_app.config)
        
        if not all([mail_server, mail_username, mail_password]):
            current_app.logger.error(current_app.config)
            current_app.logger.warning("邮件配置不完整，无法发送回复邮件")
            return False
        
        # 创建邮件内容
        subject = f"回复：{original_message.subject}"
        
        # HTML邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>回复：{original_message.subject}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 24px;
                }}
                .original-message {{
                    background: #f8f9fa;
                    border-left: 4px solid #007bff;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .original-message h3 {{
                    color: #495057;
                    margin-top: 0;
                    font-size: 16px;
                }}
                .original-message p {{
                    color: #6c757d;
                    margin: 5px 0;
                    font-size: 14px;
                }}
                .original-message .content {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 10px;
                    white-space: pre-wrap;
                    font-family: inherit;
                }}
                .reply-content {{
                    background: #e8f5e8;
                    border-left: 4px solid #28a745;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .reply-content h3 {{
                    color: #155724;
                    margin-top: 0;
                    font-size: 16px;
                }}
                .reply-content .content {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 10px;
                    white-space: pre-wrap;
                    font-family: inherit;
                }}
                .footer {{
                    border-top: 1px solid #e0e0e0;
                    padding-top: 20px;
                    margin-top: 30px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 消息回复</h1>
                    <p>您好 {original_message.name}，</p>
                    <p>感谢您的来信，以下是我们的回复：</p>
                </div>
                
                <div class="original-message">
                    <h3>📨 您的原始消息</h3>
                    <p><strong>主题：</strong>{original_message.subject}</p>
                    <p><strong>发送时间：</strong>{original_message.created_at.strftime('%Y年%m月%d日 %H:%M')}</p>
                    <div class="content">{original_message.message}</div>
                </div>
                
                <div class="reply-content">
                    <h3>💬 我们的回复</h3>
                    <div class="content">{reply_content}</div>
                </div>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                    <p>如有其他问题，请通过以下方式联系我们：</p>
                    <p>
                        <a href="https://www.shiheng.info/contact">联系我们</a> | 
                        <a href="https://www.shiheng.info">访问网站</a>
                    </p>
                    <p style="margin-top: 15px; font-size: 12px; color: #999;">
                        回复时间：{reply_record.created_at.strftime('%Y年%m月%d日 %H:%M') if reply_record else '刚刚'}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本邮件内容
        text_content = f"""
回复：{original_message.subject}

您好 {original_message.name}，

感谢您的来信，以下是我们的回复：

您的原始消息：
主题：{original_message.subject}
发送时间：{original_message.created_at.strftime('%Y年%m月%d日 %H:%M')}

{original_message.message}

我们的回复：
{reply_content}

---
此邮件由系统自动发送，请勿直接回复。
如有其他问题，请访问：https://www.shiheng.info/contact

回复时间：{reply_record.created_at.strftime('%Y年%m月%d日 %H:%M') if reply_record else '刚刚'}
        """
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = original_message.email
        
        # 添加文本和HTML内容
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # 发送邮件
        try:
            # 根据配置选择SMTP连接方式
            mail_use_ssl = current_app.config.get('MAIL_USE_SSL', False)
            mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            
            if mail_use_ssl:
                # 使用SSL连接
                server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=30)
            else:
                # 使用普通连接，然后启用TLS
                server = smtplib.SMTP(mail_server, mail_port, timeout=30)
                if mail_use_tls:
                    server.starttls()
            
            # 登录
            server.login(mail_username, mail_password)
            
            # 发送邮件
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"回复邮件发送成功：{original_message.email}")
            return True
            
        except smtplib.SMTPConnectError as e:
            current_app.logger.error(f"SMTP连接失败: {e}")
            return False
        except smtplib.SMTPAuthenticationError as e:
            current_app.logger.error(f"SMTP认证失败: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            current_app.logger.error(f"收件人被拒绝: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            current_app.logger.error(f"SMTP服务器断开连接: {e}")
            return False
        except Exception as e:
            current_app.logger.error(f"SMTP发送异常: {e}")
            return False
        
    except Exception as e:
        current_app.logger.error(f"发送回复邮件失败：{e}", exc_info=True)
        return False

def send_notification_email(user_email, user_name, notification_title, notification_content):
    """
    发送通知邮件给用户
    
    Args:
        user_email: 用户邮箱
        user_name: 用户姓名
        notification_title: 通知标题
        notification_content: 通知内容
    
    Returns:
        bool: 发送是否成功
    """
    try:
        # 检查邮件配置
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_from = current_app.config.get('MAIL_FROM', 'noreply@example.com')
        
        if not all([mail_server, mail_username, mail_password]):
            current_app.logger.warning("邮件配置不完整，无法发送通知邮件")
            return False
        
        # 创建邮件内容
        subject = f"通知：{notification_title}"
        
        # HTML邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{notification_title}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #f8f9fa;
                    border-left: 4px solid #007bff;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 5px;
                    white-space: pre-wrap;
                }}
                .footer {{
                    border-top: 1px solid #e0e0e0;
                    padding-top: 20px;
                    margin-top: 30px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 系统通知</h1>
                    <p>您好 {user_name}，</p>
                </div>
                
                <div class="content">
                    <h3>{notification_title}</h3>
                    <p>{notification_content}</p>
                </div>
                
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿直接回复。</p>
                    <p>
                        <a href="https://www.shiheng.info">访问网站</a> | 
                        <a href="https://www.shiheng.info/contact">联系我们</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本邮件内容
        text_content = f"""
{notification_title}

您好 {user_name}，

{notification_content}

---
此邮件由系统自动发送，请勿直接回复。
访问网站：https://www.shiheng.info
        """
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = user_email
        
        # 添加文本和HTML内容
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # 发送邮件
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        current_app.logger.info(f"通知邮件发送成功：{user_email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"发送通知邮件失败：{e}", exc_info=True)
        return False
