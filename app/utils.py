import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask import current_app

def send_password_reset_email(to_email, new_password):
    """
    发送密码重置邮件 (使用163邮箱)
    """
    try:
        mail_host = current_app.config['MAIL_SERVER']
        mail_port = current_app.config['MAIL_PORT']
        mail_user = current_app.config['MAIL_USERNAME']
        mail_pass = current_app.config['MAIL_PASSWORD']
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        
        # 检查是否配置了真实邮箱，如果没有则回退到模拟发送
        if mail_user == 'your_email@163.com':
            print(f"\n========== MOCK EMAIL (未配置真实邮箱) ==========")
            print(f"To: {to_email}")
            print(f"New Password: {new_password}")
            print(f"================================================\n")
            return True

        message = MIMEText(f"""
        亲爱的用户，

        您的密码重置申请已通过审批。
        您的新密码是：{new_password}
        
        请尽快登录系统并修改密码。
        
        宿舍管理系统
        """, 'plain', 'utf-8')
        
        # 正确设置发件人格式： 显示名称 <邮箱地址>
        message['From'] = formataddr((str(Header("宿舍管理系统", 'utf-8')), sender))
        message['To'] =  Header("用户", 'utf-8')
        message['Subject'] = Header("密码重置通知 - 宿舍管理系统", 'utf-8')
        
        if current_app.config['MAIL_USE_SSL']:
            smtp_obj = smtplib.SMTP_SSL(mail_host, mail_port)
        else:
            smtp_obj = smtplib.SMTP(mail_host, mail_port)
            
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, [to_email], message.as_string())
        smtp_obj.quit()
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False
