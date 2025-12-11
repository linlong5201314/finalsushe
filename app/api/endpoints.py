from flask import jsonify, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app.api import api_bp
from app import db, csrf
from app.models.models import User, Student, Repair, UtilityBill, Visitor, Dormitory, DormChangeRequest, Payment, DormManager, InvitationCode, PasswordResetRequest
from werkzeug.security import generate_password_hash
import os, qrcode

# CSRF 豁免
csrf.exempt(api_bp)

# 认证
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data: return jsonify({'code':400,'msg':'Missing JSON data'}),400
    username = data.get('username'); password = data.get('password'); user_type = data.get('userType')
    if not username or not password: return jsonify({'code':400,'msg':'Missing username or password'}),400
    user = User.query.filter_by(username=username, role=user_type).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        info = {}
        if user.role=='student' and user.student:
            info = {
                'name': user.student.name,
                'student_id': user.student.student_id,
                'dorm_id': user.student.dorm_id,
                'dorm_number': user.student.dormitory.dorm_number if user.student.dormitory else None
            }
        return jsonify({'code':200,'msg':'Login successful','data':{'user_id':user.id,'username':user.username,'role':user.role,'info':info}})
    return jsonify({'code':401,'msg':'Invalid username or password'}),401

@api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'code':200,'msg':'Logged out successfully'})

# 学生信息
@api_bp.route('/student/info', methods=['GET'])
@login_required
def student_info():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    s = current_user.student
    if not s: return jsonify({'code':404,'msg':'Student profile not found'}),404
    d = s.dormitory
    return jsonify({'code':200,'data':{
        'name': s.name, 'student_id': s.student_id, 'gender': s.gender, 'major': s.major, 'grade': s.grade, 'phone': s.phone,
        'photo': s.photo if s.photo else None,
        'dorm': {'number': d.dorm_number if d else '未分配','building': d.building if d else '', 'floor': d.floor if d else ''}
    }})

# 注册辅助：楼栋列表
@api_bp.route('/buildings', methods=['GET'])
def buildings():
    buildings = db.session.query(Dormitory.building).distinct().all()
    return jsonify({'code':200,'data':[b[0] for b in buildings]})

# 注册
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    user_type = data.get('userType')
    phone = data.get('phone')
    invitation_code = data.get('invitation_code')
    responsible_building = data.get('responsible_building')

    if not all([username, name, password, confirm_password, user_type, phone]):
        return jsonify({'code':400,'msg':'缺少必要字段'}),400
    if password != confirm_password:
        return jsonify({'code':400,'msg':'两次输入的密码不一致'}),400
    if User.query.filter_by(username=username).first():
        return jsonify({'code':400,'msg':'学号/工号已存在'}),400
    if email and User.query.filter_by(email=email).first():
        return jsonify({'code':400,'msg':'邮箱已存在'}),400

    if user_type == 'admin':
        return jsonify({'code':400,'msg':'管理员账号不允许注册'}),400
    if user_type == 'dorm_manager':
        if not responsible_building:
            return jsonify({'code':400,'msg':'请输入负责楼栋'}),400
        record = InvitationCode.query.filter_by(code=invitation_code, is_used=False).first()
        if not record:
            return jsonify({'code':400,'msg':'无效或已使用的邀请码'}),400

    user = User(username=username, email=email, password=generate_password_hash(password), role=user_type)
    db.session.add(user); db.session.flush()
    if user_type == 'student':
        student = Student(user_id=user.id, student_id=username, name=name, gender='男', major='未分配', grade='未分配', phone=phone)
        db.session.add(student)
    elif user_type == 'dorm_manager':
        dm = DormManager(user_id=user.id, name=name, phone=phone, responsible_building=responsible_building)
        db.session.add(dm)
        # 标记邀请码已使用
        if invitation_code:
            record = InvitationCode.query.filter_by(code=invitation_code, is_used=False).first()
            if record:
                from datetime import datetime
                record.is_used = True
                record.used_at = datetime.now()
    db.session.commit()
    return jsonify({'code':200,'msg':'注册成功'})

# 忘记密码申请
@api_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    if not email or not name:
        return jsonify({'code':400,'msg':'缺少邮箱或姓名'}),400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'code':404,'msg':'该邮箱未注册'}),404
    # 验证姓名
    is_valid = False
    if user.role == 'student' and user.student and user.student.name == name:
        is_valid = True
    elif user.role == 'dorm_manager' and user.dorm_manager and user.dorm_manager.name == name:
        is_valid = True
    elif user.role == 'admin':
        is_valid = True
    if not is_valid:
        return jsonify({'code':400,'msg':'姓名与注册邮箱不匹配'}),400
    existing = PasswordResetRequest.query.filter_by(user_id=user.id, status='pending').first()
    if not existing:
        req = PasswordResetRequest(user_id=user.id)
        db.session.add(req); db.session.commit()
        return jsonify({'code':200,'msg':'密码重置请求已提交，请等待审核'})
    return jsonify({'code':200,'msg':'您已提交过申请，请耐心等待'})

@api_bp.route('/student/dorm', methods=['GET'])
@login_required
def student_dorm():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    s = current_user.student
    if not s.dorm_id: return jsonify({'code':404,'msg':'No dormitory assigned'}),404
    d = Dormitory.query.get(s.dorm_id)
    roommates = Student.query.filter(Student.dorm_id==d.id, Student.id!=s.id).all()
    return jsonify({'code':200,'data':{
        'dorm_info': {'number': d.dorm_number, 'building': d.building, 'floor': d.floor, 'capacity': d.capacity, 'current_occupancy': d.current_occupancy},
        'roommates': [{'name': r.name,'student_id': r.student_id,'major': r.major,'grade': r.grade,'phone': r.phone} for r in roommates]
    }})

@api_bp.route('/student/photo', methods=['POST'])
@login_required
def upload_photo():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    if 'photo' not in request.files: return jsonify({'code':400,'msg':'No file part'}),400
    file = request.files['photo']
    if file.filename=='': return jsonify({'code':400,'msg':'No selected file'}),400
    s = current_user.student
    folder = os.path.join(current_app.root_path, 'static', 'uploads'); os.makedirs(folder, exist_ok=True)
    filename = secure_filename(file.filename); ext = os.path.splitext(filename)[1].lower()
    new_name = f'student_{s.id}{ext}'; path = os.path.join(folder, new_name); file.save(path)
    s.photo = f'uploads/{new_name}'; db.session.commit()
    return jsonify({'code':200,'msg':'Photo uploaded','url': s.photo})

# 报修
@api_bp.route('/repairs', methods=['GET'])
@login_required
def repairs_list():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    arr = Repair.query.filter_by(student_id=current_user.student.id).order_by(Repair.created_at.desc()).all()
    data=[{'id':r.id,'title':r.title,'content':r.content,'status':r.status,'created_at':r.created_at.strftime('%Y-%m-%d %H:%M'),'location_type':r.location_type,'repair_type':r.repair_type} for r in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/repairs', methods=['POST'])
@login_required
def repairs_create():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    data = request.get_json(); required=['title','content','location_type','repair_type','location_detail','contact_phone']
    for f in required:
        if not data.get(f): return jsonify({'code':400,'msg':f'Missing field: {f}'}),400
    r = Repair(student_id=current_user.student.id, dorm_id=current_user.student.dorm_id, title=data['title'], content=data['content'], location_type=data['location_type'], repair_type=data['repair_type'], location_detail=data['location_detail'], contact_phone=data['contact_phone'], urgent_level=data.get('urgent_level','normal'))
    db.session.add(r); db.session.commit(); return jsonify({'code':200,'msg':'Repair request submitted'})

# 水电费
@api_bp.route('/utility_bills', methods=['GET'])
@login_required
def bills():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    if not current_user.student.dorm_id: return jsonify({'code':200,'data':[]})
    arr = UtilityBill.query.filter_by(dorm_id=current_user.student.dorm_id).order_by(UtilityBill.month.desc()).all()
    data=[{'id':b.id,'month':b.month,'electricity':b.electricity,'water':b.water,'total_cost':b.total_cost,'status':b.status,'due_date':b.due_date.strftime('%Y-%m-%d')} for b in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/utility_bills/pay', methods=['POST'])
@login_required
def bills_pay():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    data = request.get_json(); bill_id = data.get('bill_id'); method = data.get('payment_method','wechat')
    if not bill_id: return jsonify({'code':400,'msg':'Missing bill_id'}),400
    bill = UtilityBill.query.get(bill_id)
    if not bill: return jsonify({'code':404,'msg':'Bill not found'}),404
    if bill.dorm_id != current_user.student.dorm_id: return jsonify({'code':403,'msg':'Permission denied'}),403
    if bill.status=='paid': return jsonify({'code':400,'msg':'Bill already paid'}),400
    p = Payment(bill_id=bill.id, student_id=current_user.student.id, amount=bill.total_cost, payment_method=method, payment_status='completed')
    db.session.add(p); bill.status='paid'; db.session.commit(); return jsonify({'code':200,'msg':'Payment successful'})

# 访客
@api_bp.route('/visitors', methods=['GET'])
@login_required
def visitors_list():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    arr = Visitor.query.filter_by(student_id=current_user.student.id).order_by(Visitor.visit_date.desc()).all()
    data=[{'id':v.id,'name':v.name,'visit_date':v.visit_date.strftime('%Y-%m-%d %H:%M'),'purpose':v.purpose,'status':v.status,'qr_code':v.qr_code} for v in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/visitors', methods=['POST'])
@login_required
def visitors_create():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    data = request.get_json(); req=['name','id_card','phone','purpose','dorm_number']
    for f in req:
        if not data.get(f): return jsonify({'code':400,'msg':f'Missing field: {f}'}),400
    s = current_user.student
    v = Visitor(name=data['name'], id_card=data['id_card'], phone=data['phone'], purpose=data['purpose'], dorm_number=data['dorm_number'], student_name=s.name, student_id=s.id)
    db.session.add(v); db.session.flush()
    qr_data = f"visitor_id={v.id}&name={v.name}&id_card={v.id_card}&visit_date={v.visit_date.strftime('%Y-%m-%d %H:%M:%S')}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4); qr.add_data(qr_data); qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    folder = os.path.join(current_app.root_path,'static','qr_codes'); os.makedirs(folder, exist_ok=True)
    fname = f"visitor_{v.id}.png"; path = os.path.join(folder, fname); img.save(path)
    v.qr_code = f"qr_codes/{fname}"; db.session.commit(); return jsonify({'code':200,'msg':'Visitor registered','qr_code':v.qr_code})

# 调宿申请
@api_bp.route('/dorm_changes', methods=['GET'])
@login_required
def dorm_changes_list():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    arr = DormChangeRequest.query.filter_by(student_id=current_user.student.id).order_by(DormChangeRequest.created_at.desc()).all()
    data=[{'id':r.id,'current_dorm_id':r.current_dorm_id,'target_dorm_id':r.target_dorm_id,'reason':r.reason,'status':r.status,'created_at':r.created_at.strftime('%Y-%m-%d')} for r in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/dorm_changes', methods=['POST'])
@login_required
def dorm_changes_create():
    if current_user.role!='student': return jsonify({'code':403,'msg':'Permission denied'}),403
    data = request.get_json();
    if not data.get('reason'): return jsonify({'code':400,'msg':'Reason is required'}),400
    req = DormChangeRequest(student_id=current_user.student.id, current_dorm_id=current_user.student.dorm_id, target_dorm_id=data.get('target_dorm_id'), reason=data.get('reason'))
    db.session.add(req); db.session.commit(); return jsonify({'code':200,'msg':'Request submitted'})

# 宿管端（代表性接口）
@api_bp.route('/dm/dashboard', methods=['GET'])
@login_required
def dm_dashboard():
    if current_user.role!='dorm_manager': return jsonify({'code':403,'msg':'Permission denied'}),403
    dm = DormManager.query.filter_by(user_id=current_user.id).first()
    total_students = Student.query.join(Dormitory).filter(Dormitory.building==dm.responsible_building).count()
    total_dorms = Dormitory.query.filter_by(building=dm.responsible_building).count()
    pending_repairs = Repair.query.join(Dormitory, Repair.dorm_id==Dormitory.id).filter(Dormitory.building==dm.responsible_building, Repair.status=='pending').count()
    current_visitors = Visitor.query.join(Student).join(Dormitory).filter(Dormitory.building==dm.responsible_building, Visitor.status=='in').count()
    return jsonify({'code':200,'data':{'total_students':total_students,'total_dorms':total_dorms,'pending_repairs':pending_repairs,'current_visitors':current_visitors}})

@api_bp.route('/dm/students', methods=['GET'])
@login_required
def dm_students():
    if current_user.role!='dorm_manager': return jsonify({'code':403,'msg':'Permission denied'}),403
    dm = DormManager.query.filter_by(user_id=current_user.id).first()
    arr = Student.query.join(Dormitory).filter(Dormitory.building==dm.responsible_building, Student.is_deleted==False).all()
    data=[{'name':s.name,'student_id':s.student_id,'major':s.major,'grade':s.grade,'phone':s.phone,'dorm_id':s.dorm_id} for s in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/dm/dormitories', methods=['GET'])
@login_required
def dm_dorms():
    if current_user.role!='dorm_manager': return jsonify({'code':403,'msg':'Permission denied'}),403
    dm = DormManager.query.filter_by(user_id=current_user.id).first()
    arr = Dormitory.query.filter_by(building=dm.responsible_building).all()
    data=[{'id':d.id,'number':d.dorm_number,'building':d.building,'floor':d.floor,'capacity':d.capacity,'current_occupancy':d.current_occupancy} for d in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/dm/repairs', methods=['GET'])
@login_required
def dm_repairs():
    if current_user.role!='dorm_manager': return jsonify({'code':403,'msg':'Permission denied'}),403
    dm = DormManager.query.filter_by(user_id=current_user.id).first()
    arr = Repair.query.join(Dormitory, Repair.dorm_id==Dormitory.id).filter(Dormitory.building==dm.responsible_building, Repair.is_deleted==False).all()
    data=[{'id':r.id,'title':r.title,'status':r.status,'student_id':r.student_id} for r in arr]
    return jsonify({'code':200,'data':data})

@api_bp.route('/dm/repairs/process', methods=['POST'])
@login_required
def dm_process_repair():
    if current_user.role!='dorm_manager': return jsonify({'code':403,'msg':'Permission denied'}),403
    rid = request.get_json().get('repair_id'); status = request.get_json().get('status')
    r = Repair.query.get(rid)
    if not r: return jsonify({'code':404,'msg':'Record not found'}),404
    r.status = status; db.session.commit(); return jsonify({'code':200,'msg':'Updated'})

# 管理员端接口可按需扩展（列表/新增/编辑/删除/统计），与现有视图逻辑一致
