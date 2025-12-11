from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.models import User, InvitationCode, PasswordResetRequest, Dormitory
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['userType']
        
        user = User.query.filter_by(username=username, role=user_type).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('登录成功！', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'dorm_manager':
                return redirect(url_for('dorm_manager.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('用户名、密码或用户类型错误！', 'danger')
    
    # 获取楼栋列表供注册使用
    buildings = db.session.query(Dormitory.building).distinct().all()
    buildings = [b[0] for b in buildings]
    
    return render_template('login.html', buildings=buildings)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录！', 'success')
    return redirect(url_for('main.login'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['userType']
        phone = request.form['phone']
        
        # 验证宿管邀请码和负责楼栋
        invitation_code_record = None
        responsible_building = None
        if user_type == 'dorm_manager':
            code = request.form.get('invitation_code')
            responsible_building = request.form.get('responsible_building')
            
            if not responsible_building:
                flash('请输入负责楼栋！', 'danger')
                return redirect(url_for('main.login'))
                
            invitation_code_record = InvitationCode.query.filter_by(code=code, is_used=False).first()
            if not invitation_code_record:
                flash('无效或已使用的邀请码！', 'danger')
                return redirect(url_for('main.login'))

        # 验证密码
        if password != confirm_password:
            flash('两次输入的密码不一致！', 'danger')
        else:
            # 检查用户名和邮箱是否已存在
            if User.query.filter_by(username=username).first():
                flash('学号/工号已存在！', 'danger')
            elif User.query.filter_by(email=email).first():
                flash('邮箱已存在！', 'danger')
            else:
                # 创建用户
                user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    role=user_type
                )
                
                db.session.add(user)
                db.session.flush()  # 获取用户ID
                
                # 根据用户类型创建对应的信息
                if user_type == 'student':
                    from app.models.models import Student
                    student = Student(
                        user_id=user.id,
                        student_id=username,  # 使用用户名作为学号
                        name=name,
                        gender='男',  # 默认值，后续可以修改
                        major='未分配',  # 默认值
                        grade='未分配',  # 默认值
                        phone=phone
                    )
                    db.session.add(student)
                elif user_type == 'dorm_manager':
                    from app.models.models import DormManager
                    dorm_manager = DormManager(
                        user_id=user.id,
                        name=name,
                        phone=phone,
                        responsible_building=responsible_building
                    )
                    db.session.add(dorm_manager)
                    
                    # 标记邀请码已使用
                    if invitation_code_record:
                        invitation_code_record.is_used = True
                        invitation_code_record.used_at = datetime.now()
                
                db.session.commit()
                
                flash('注册成功！请登录', 'success')
                return redirect(url_for('main.login'))
    
    # 获取楼栋列表供注册使用
    buildings = db.session.query(Dormitory.building).distinct().all()
    buildings = [b[0] for b in buildings]
    
    return render_template('login.html', buildings=buildings)

@main_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        
        # 通过邮箱查找用户
        user = User.query.filter_by(email=email).first()
        if user:
            # 验证姓名是否匹配
            is_valid = False
            if user.role == 'student':
                if user.student and user.student.name == name:
                    is_valid = True
            elif user.role == 'dorm_manager':
                if user.dorm_manager and user.dorm_manager.name == name:
                    is_valid = True
            elif user.role == 'admin':
                # 管理员没有关联的student或dorm_manager表，假设验证通过
                is_valid = True
            
            if is_valid:
                # 检查是否有待处理的请求
                existing_req = PasswordResetRequest.query.filter_by(user_id=user.id, status='pending').first()
                if not existing_req:
                    req = PasswordResetRequest(user_id=user.id)
                    db.session.add(req)
                    db.session.commit()
                    flash('密码重置请求已提交，请联系管理员或宿管审核！', 'success')
                else:
                    flash('您已提交过申请，请耐心等待！', 'warning')
            else:
                flash('姓名与注册邮箱不匹配！', 'danger')
        else:
            flash('该邮箱未注册！', 'danger')
        
        return redirect(url_for('main.login'))
    
    return redirect(url_for('main.login'))