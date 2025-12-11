# 配置文件
import os
import tempfile

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    # 使用SQLite数据库，适合云部署
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../instance/database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 模板和静态文件配置
    TEMPLATES_AUTO_RELOAD = True
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    
    # 邮件配置 (163邮箱示例)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.163.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') == 'True' or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'm13136064359@163.com'  # 请替换为真实邮箱
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'XSTKpwH3WgtcPmiP'      # 请替换为真实授权码
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'm13136064359@163.com'
