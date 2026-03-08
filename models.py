from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Admin user model"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    college_name = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    certificates = db.relationship('Certificate', backref='creator', lazy='dynamic')
    college_config = db.relationship('CollegeConfig', backref='user', uselist=False)

class CollegeConfig(db.Model):
    """College configuration with images"""
    __tablename__ = 'college_config'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    college_name = db.Column(db.String(255), nullable=False)
    college_logo = db.Column(db.String(500))
    founder_image = db.Column(db.String(500))
    principal_signature = db.Column(db.String(500))
    secretary_signature = db.Column(db.String(500))
    
    principal_name = db.Column(db.String(255))
    secretary_name = db.Column(db.String(255))
    founder_name = db.Column(db.String(255))
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Certificate(db.Model):
    """Certificate record"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    student_name = db.Column(db.String(255), nullable=False, index=True)
    roll_no = db.Column(db.String(50))
    event_name = db.Column(db.String(255), nullable=False)
    event_category = db.Column(db.String(50))
    position = db.Column(db.String(100))
    event_date = db.Column(db.String(50), nullable=False)
    
    college_name = db.Column(db.String(255), nullable=False)
    certificate_file = db.Column(db.String(500))
    qr_code = db.Column(db.String(500))
    
    status = db.Column(db.String(50), default='generated')
    email_sent = db.Column(db.Boolean, default=False)
    student_email = db.Column(db.String(120))
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    verified_at = db.Column(db.DateTime)

class BatchUpload(db.Model):
    """Batch upload records"""
    __tablename__ = 'batch_uploads'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    filename = db.Column(db.String(255), nullable=False)
    total_records = db.Column(db.Integer, default=0)
    processed_records = db.Column(db.Integer, default=0)
    failed_records = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(50), default='processing')
    error_message = db.Column(db.Text)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
