from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Student, Repair, Dormitory, Visitor, DormChangeRequest, UtilityBill, Payment
import os
import qrcode
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('student/dashboard.html', student=student)

@student_bp.route('/my_info', methods=['GET', 'POST'])
@login_required
def my_info():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # 处理照片上传
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                # 确保上传目录存在
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # 保存文件
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()
                new_filename = f'student_{student.id}{file_ext}'
                file_path = os.path.join(upload_folder, new_filename)
                file.save(file_path)
                
                # 更新学生照片路径
                student.photo = f'uploads/{new_filename}'
                db.session.commit()
                flash('照片上传成功！', 'success')
    
    return render_template('student/my_info.html', student=student)

@student_bp.route('/my_dorm')
@login_required
def my_dorm():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    dorm = Dormitory.query.get(student.dorm_id) if student.dorm_id else None
    roommates = []
    if dorm:
        roommates = Student.query.filter(Student.dorm_id == dorm.id, Student.id != student.id).all()
    return render_template('student/my_dorm.html', student=student, dorm=dorm, roommates=roommates)

@student_bp.route('/submit_repair', methods=['GET', 'POST'])
@login_required
def submit_repair():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        location_type = request.form['location_type']
        repair_type = request.form['repair_type']
        location_detail = request.form['location_detail']
        contact_phone = request.form['contact_phone']
        urgent_level = request.form['urgent_level']
        
        repair = Repair(
            dorm_id=student.dorm_id if location_type == 'dorm' else None,
            student_id=student.id,
            title=title,
            content=content,
            location_type=location_type,
            repair_type=repair_type,
            location_detail=location_detail,
            contact_phone=contact_phone,
            urgent_level=urgent_level
        )
        
        db.session.add(repair)
        db.session.commit()
        
        flash('报修成功！', 'success')
        return redirect(url_for('student.my_repairs'))
    
    return render_template('student/submit_repair.html', student=student)

@student_bp.route('/my_repairs')
@login_required
def my_repairs():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    repairs = Repair.query.filter_by(student_id=student.id, is_deleted=False).all()
    
    return render_template('student/my_repairs.html', repairs=repairs)

@student_bp.route('/visitor_register', methods=['GET', 'POST'])
@login_required
def visitor_register():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        name = request.form['name']
        id_card = request.form['id_card']
        phone = request.form['phone']
        purpose = request.form['purpose']
        dorm_number = request.form['dorm_number']
        
        # 创建访客记录
        visitor = Visitor(
            name=name,
            id_card=id_card,
            phone=phone,
            purpose=purpose,
            dorm_number=dorm_number,
            student_name=student.name,
            student_id=student.id
        )
        
        db.session.add(visitor)
        db.session.flush()  # 获取visitor.id
        
        # 生成QR码
        qr_data = f"visitor_id={visitor.id}&name={name}&id_card={id_card}&visit_date={visitor.visit_date.strftime('%Y-%m-%d %H:%M:%S')}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存QR码图片
        qr_folder = os.path.join(current_app.root_path, 'static', 'qr_codes')
        os.makedirs(qr_folder, exist_ok=True)
        qr_filename = f"visitor_{visitor.id}.png"
        qr_path = os.path.join(qr_folder, qr_filename)
        img.save(qr_path)
        
        # 更新访客记录的QR码路径
        visitor.qr_code = f"qr_codes/{qr_filename}"
        
        db.session.commit()
        
        flash('访客登记成功！', 'success')
        return redirect(url_for('student.my_visitors'))
    
    return render_template('student/visitor_register.html', student=student)

@student_bp.route('/my_visitors')
@login_required
def my_visitors():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    visitors = Visitor.query.filter_by(student_id=student.id, is_deleted=False).all()
    
    return render_template('student/my_visitors.html', visitors=visitors)

@student_bp.route('/submit_dorm_change', methods=['GET', 'POST'])
@login_required
def submit_dorm_change():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        target_dorm_id = request.form.get('target_dorm_id')
        reason = request.form['reason']
        
        # 创建宿舍调换申请
        dorm_change_request = DormChangeRequest(
            student_id=student.id,
            current_dorm_id=student.dorm_id,
            target_dorm_id=target_dorm_id if target_dorm_id else None,
            reason=reason
        )
        
        db.session.add(dorm_change_request)
        db.session.commit()
        
        flash('宿舍调换申请已提交！', 'success')
        return redirect(url_for('student.my_dorm'))
    
    # 获取可选的宿舍列表（同性别、未满员的宿舍）
    available_dorms = Dormitory.query.filter(
        Dormitory.gender == student.gender,
        Dormitory.current_occupancy < Dormitory.capacity,
        Dormitory.id != student.dorm_id
    ).all()
    
    return render_template('student/submit_dorm_change.html', student=student, available_dorms=available_dorms)

@student_bp.route('/my_dorm_change_requests')
@login_required
def my_dorm_change_requests():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    requests = DormChangeRequest.query.filter_by(student_id=student.id).order_by(DormChangeRequest.created_at.desc()).all()
    
    return render_template('student/my_dorm_change_requests.html', requests=requests)

@student_bp.route('/my_utility_bills')
@login_required
def my_utility_bills():
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # 获取学生宿舍的水电费账单
    bills = UtilityBill.query.join(Dormitory, UtilityBill.dorm_id == Dormitory.id).join(Student, Dormitory.id == Student.dorm_id).filter(Student.id == student.id).all()
    
    return render_template('student/my_utility_bills.html', bills=bills, student=student)

@student_bp.route('/pay_utility_bill/<int:bill_id>', methods=['GET', 'POST'])
@login_required
def pay_utility_bill(bill_id):
    if current_user.role != 'student':
        flash('无权访问！', 'danger')
        return redirect(url_for('main.login'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    bill = UtilityBill.query.get_or_404(bill_id)
    
    # 检查账单是否属于该学生
    if bill.dormitory.students.filter_by(id=student.id).first() is None:
        flash('无权访问该账单！', 'danger')
        return redirect(url_for('student.my_utility_bills'))
    
    if request.method == 'POST':
        # 检查是否已支付
        if bill.status == 'paid':
            flash('该账单已支付！', 'warning')
            return redirect(url_for('student.my_utility_bills'))

        try:
            amount = float(request.form['amount'])
            payment_method = request.form['payment_method']
            
            # 简单验证金额
            if abs(amount - bill.total_cost) > 0.01:
                flash('支付金额不正确！', 'danger')
                return redirect(url_for('student.pay_utility_bill', bill_id=bill_id))
            
            # 创建支付记录
            payment = Payment(
                bill_id=bill.id,
                student_id=student.id,
                amount=amount,
                payment_method=payment_method,
                payment_status='completed'  # 模拟支付成功
            )
            db.session.add(payment)
            
            # 更新账单状态
            bill.status = 'paid'
            db.session.commit()
            
            flash('支付成功！', 'success')
            return redirect(url_for('student.my_utility_bills'))
            
        except ValueError:
            flash('无效的支付金额！', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'支付失败：{str(e)}', 'danger')
    
    return render_template('student/pay_utility_bill.html', bill=bill, student=student)