from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config.config import Config

# 创建数据库实例
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    csrf.init_app(app)
    
    # 导入并注册蓝图
    from app.views.main import main_bp
    from app.views.admin import admin_bp
    from app.views.student import student_bp
    from app.views.dorm_manager import dorm_manager_bp
    from app.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(dorm_manager_bp, url_prefix='/dorm_manager')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
