from app import create_app, db
from flask_login import LoginManager
from app.models.models import User
import os

app = create_app()

# 配置Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 确保instance目录存在
if not os.path.exists('instance'):
    os.makedirs('instance')

# 创建数据库表
with app.app_context():
    db.create_all()
    # 检查并创建默认超级管理员
    from app.models.models import User
    from werkzeug.security import generate_password_hash
    admin = User.query.filter_by(username='123').first()
    if not admin:
        admin = User(
            username='123',
            password=generate_password_hash('123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('默认超级管理员创建成功：账号123，密码123')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')