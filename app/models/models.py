from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # 新增邮箱字段
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, student, dorm_manager
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    
    # 关系
    student = db.relationship('Student', backref='user', uselist=False)
    dorm_manager = db.relationship('DormManager', backref='user', uselist=False)
    
    # Flask-Login 必要属性和方法
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    major = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'))
    phone = db.Column(db.String(20), nullable=False)
    photo = db.Column(db.String(200), nullable=True)  # 学生照片路径
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    
    # 关系
    repairs = db.relationship('Repair', backref='student', lazy=True)
    visitors = db.relationship('Visitor', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.name}>'

class DormManager(db.Model):
    __tablename__ = 'dorm_managers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    responsible_building = db.Column(db.String(20), nullable=False)  # 负责的楼栋
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    
    def __repr__(self):
        return f'<DormManager {self.name}>'

class Dormitory(db.Model):
    __tablename__ = 'dormitories'
    
    id = db.Column(db.Integer, primary_key=True)
    dorm_number = db.Column(db.String(20), unique=True, nullable=False)
    building = db.Column(db.String(20), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    gender = db.Column(db.String(10), nullable=False)
    
    # 关系
    students = db.relationship('Student', backref='dormitory', lazy=True)
    repairs = db.relationship('Repair', backref='dormitory', lazy=True)
    
    def __repr__(self):
        return f'<Dormitory {self.dorm_number}>'

class Repair(db.Model):
    __tablename__ = 'repairs'
    
    id = db.Column(db.Integer, primary_key=True)
    dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    location_type = db.Column(db.String(50), nullable=False)  # dorm, training, teaching, other
    repair_type = db.Column(db.String(50), nullable=False)  # water, air_conditioner, furniture, network, other
    location_detail = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    urgent_level = db.Column(db.String(20), default='normal')  # normal, urgent, very_urgent
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    
    def __repr__(self):
        return f'<Repair {self.title}>'

class Visitor(db.Model):
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    id_card = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.now)
    leave_date = db.Column(db.DateTime)
    purpose = db.Column(db.Text, nullable=False)
    dorm_number = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    status = db.Column(db.String(20), default='in')  # in, out
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除标记
    qr_code = db.Column(db.String(200), nullable=True)  # 访客二维码路径
    
    def __repr__(self):
        return f'<Visitor {self.name}>'

# 新增水电费管理模块
class UtilityBill(db.Model):
    __tablename__ = 'utility_bills'
    
    id = db.Column(db.Integer, primary_key=True)
    dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # 格式：YYYY-MM
    electricity = db.Column(db.Float, default=0)  # 用电量
    water = db.Column(db.Float, default=0)  # 用水量
    electricity_cost = db.Column(db.Float, default=0)  # 电费
    water_cost = db.Column(db.Float, default=0)  # 水费
    total_cost = db.Column(db.Float, default=0)  # 总费用
    status = db.Column(db.String(20), default='unpaid')  # unpaid, paid
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    dormitory = db.relationship('Dormitory', backref='utility_bills')
    payments = db.relationship('Payment', backref='utility_bill', lazy=True)
    
    def __repr__(self):
        return f'<UtilityBill {self.dorm_id}-{self.month}>'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('utility_bills.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, wechat, alipay, bank
    payment_status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    
    # 关系
    student = db.relationship('Student', backref='payments')
    
    def __repr__(self):
        return f'<Payment {self.id}>'

# 新增宿舍调换申请
class DormChangeRequest(db.Model):
    __tablename__ = 'dorm_change_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    current_dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'), nullable=False)
    target_dorm_id = db.Column(db.Integer, db.ForeignKey('dormitories.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 审批人ID
    
    # 关系
    student = db.relationship('Student', backref='dorm_change_requests')
    current_dorm = db.relationship('Dormitory', foreign_keys=[current_dorm_id], backref='current_dorm_change_requests')
    target_dorm = db.relationship('Dormitory', foreign_keys=[target_dorm_id], backref='target_dorm_change_requests')
    approver = db.relationship('User', backref='approved_dorm_changes')
    
    def __repr__(self):
        return f'<DormChangeRequest {self.id}>'

# 新增邀请码模型
class InvitationCode(db.Model):
    __tablename__ = 'invitation_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    used_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    creator = db.relationship('User', backref='created_invitation_codes')

    def __repr__(self):
        return f'<InvitationCode {self.code}>'

# 新增密码重置申请模型
class PasswordResetRequest(db.Model):
    __tablename__ = 'password_reset_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, rejected
    request_time = db.Column(db.DateTime, default=datetime.now)
    handled_at = db.Column(db.DateTime, nullable=True)
    handled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='password_reset_requests')
    handler = db.relationship('User', foreign_keys=[handled_by], backref='handled_password_resets')

    def __repr__(self):
        return f'<PasswordResetRequest {self.user_id}>'
