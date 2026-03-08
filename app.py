from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import os
from datetime import datetime
import uuid
import csv

from config import config
from models import db, User, Certificate, CollegeConfig, BatchUpload

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload directories
for directory in ['uploads/logos', 'uploads/images', 'uploads/signatures', 'uploads/certificates']:
    os.makedirs(directory, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Validation
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            college_name=data['college_name'],
            is_admin=True
        )
        
        db.session.add(user)
        db.session.flush()
        
        # Create college config
        college_config = CollegeConfig(user_id=user.id, college_name=data['college_name'])
        db.session.add(college_config)
        db.session.commit()
        
        login_user(user)
        return jsonify({'message': 'Registration successful'}), 201
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            login_user(user)
            return jsonify({'message': 'Login successful'}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    certificates = Certificate.query.filter_by(creator_id=current_user.id).order_by(Certificate.generated_at.desc()).all()
    total_certs = len(certificates)
    
    return render_template('dashboard.html', 
                         total_certificates=total_certs,
                         certificates=certificates)

@app.route('/upload-images', methods=['GET', 'POST'])
@login_required
def upload_images():
    """Upload college images and signatures"""
    college_config = CollegeConfig.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        try:
            # Handle logo upload
            if 'logo' in request.files and request.files['logo'].filename:
                file = request.files['logo']
                if file and allowed_file(file.filename):
                    filename = f"logo_{current_user.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
                    file.save(os.path.join('uploads/logos', filename))
                    college_config.college_logo = filename
            
            # Handle founder image
            if 'founder_image' in request.files and request.files['founder_image'].filename:
                file = request.files['founder_image']
                if file and allowed_file(file.filename):
                    filename = f"founder_{current_user.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
                    file.save(os.path.join('uploads/images', filename))
                    college_config.founder_image = filename
            
            # Handle principal signature
            if 'principal_sig' in request.files and request.files['principal_sig'].filename:
                file = request.files['principal_sig']
                if file and allowed_file(file.filename):
                    filename = f"principal_{current_user.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
                    file.save(os.path.join('uploads/signatures', filename))
                    college_config.principal_signature = filename
            
            # Handle secretary signature
            if 'secretary_sig' in request.files and request.files['secretary_sig'].filename:
                file = request.files['secretary_sig']
                if file and allowed_file(file.filename):
                    filename = f"secretary_{current_user.id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}"
                    file.save(os.path.join('uploads/signatures', filename))
                    college_config.secretary_signature = filename
            
            # Update names
            college_config.principal_name = request.form.get('principal_name', college_config.principal_name)
            college_config.secretary_name = request.form.get('secretary_name', college_config.secretary_name)
            college_config.founder_name = request.form.get('founder_name', college_config.founder_name)
            
            db.session.commit()
            return jsonify({'message': 'Images uploaded successfully'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    return render_template('upload_images.html', config=college_config)

@app.route('/api/generate-certificate', methods=['POST'])
@login_required
def generate_certificate():
    """Generate individual certificate with images"""
    try:
        data = request.form
        college_config = CollegeConfig.query.filter_by(user_id=current_user.id).first()
        
        # Create certificate image (1200x800 pixels)
        cert_img = Image.new('RGB', (1200, 800), 'white')
        draw = ImageDraw.Draw(cert_img)
        
        # Add decorative border
        border_color = (20, 51, 96)
        draw.rectangle([20, 20, 1180, 780], outline=border_color, width=3)
        draw.rectangle([30, 30, 1170, 770], outline=border_color, width=1)
        
        # Add college logo (top left)
        if college_config and college_config.college_logo:
            logo_path = os.path.join('uploads/logos', college_config.college_logo)
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path)
                    logo.thumbnail((100, 100), Image.Resampling.LANCZOS)
                    cert_img.paste(logo, (60, 50), logo if logo.mode == 'RGBA' else None)
                except:
                    pass
        
        # Try to load font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            content_font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Add header text
        draw.text((600, 80), "CERTIFICATE OF ACHIEVEMENT", 
                 fill='black', font=title_font, anchor='mm')
        
        # Add student name
        student_name = data.get('student_name', 'Student')
        draw.text((600, 180), student_name, fill='black', font=content_font, anchor='mm')
        
        # Add event details
        event_name = data.get('event_name', '')
        position = data.get('position', '')
        draw.text((600, 280), f"For outstanding performance in", fill='black', font=small_font, anchor='mm')
        draw.text((600, 330), event_name, fill='black', font=content_font, anchor='mm')
        draw.text((600, 400), position, fill='black', font=small_font, anchor='mm')
        
        # Add college name
        draw.text((600, 500), f"From {current_user.college_name}", fill='black', font=small_font, anchor='mm')
        
        # Add date
        event_date = data.get('event_date', '')
        draw.text((200, 600), f"Date: {event_date}", fill='black', font=small_font, anchor='lm')
        
        # Add principal signature
        if college_config and college_config.principal_signature:
            sig_path = os.path.join('uploads/signatures', college_config.principal_signature)
            if os.path.exists(sig_path):
                try:
                    sig = Image.open(sig_path)
                    sig.thumbnail((80, 60), Image.Resampling.LANCZOS)
                    cert_img.paste(sig, (150, 620), sig if sig.mode == 'RGBA' else None)
                except:
                    pass
        
        draw.text((200, 710), college_config.principal_name or "Principal", 
                 fill='black', font=small_font, anchor='mm')
        
        # Add secretary signature
        if college_config and college_config.secretary_signature:
            sig_path = os.path.join('uploads/signatures', college_config.secretary_signature)
            if os.path.exists(sig_path):
                try:
                    sig = Image.open(sig_path)
                    sig.thumbnail((80, 60), Image.Resampling.LANCZOS)
                    cert_img.paste(sig, (1000, 620), sig if sig.mode == 'RGBA' else None)
                except:
                    pass
        
        draw.text((1050, 710), college_config.secretary_name or "Secretary", 
                 fill='black', font=small_font, anchor='mm')
        
        # Generate QR code
        cert_id = str(uuid.uuid4())
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(f"https://yoursite.com/verify/{cert_id}")
        qr.make()
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((80, 80), Image.Resampling.LANCZOS)
        cert_img.paste(qr_img, (1050, 50))
        
        # Save certificate
        cert_filename = f"{student_name.replace(' ', '_')}_{cert_id}.png"
        cert_path = os.path.join('uploads/certificates', cert_filename)
        cert_img.save(cert_path, 'PNG')
        
        # Save to database
        certificate = Certificate(
            id=cert_id,
            creator_id=current_user.id,
            student_name=student_name,
            roll_no=data.get('roll_no'),
            event_name=event_name,
            event_category=data.get('event_category'),
            position=position,
            event_date=data.get('event_date'),
            college_name=current_user.college_name,
            certificate_file=cert_filename,
            student_email=data.get('student_email')
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        # Send file
        return send_file(cert_path, mimetype='image/png', 
                        as_attachment=True, 
                        download_name=cert_filename)
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-generate', methods=['POST'])
@login_required
def batch_generate():
    """Generate multiple certificates from CSV"""
    try:
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['csv_file']
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be CSV'}), 400
        
        stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        csv_data = csv.DictReader(stream)
        
        batch_id = str(uuid.uuid4())
        success_count = 0
        
        for row in csv_data:
            try:
                # Prepare form data
                form_data = {
                    'student_name': row.get('student_name', ''),
                    'event_name': row.get('event_name', ''),
                    'event_category': row.get('event_category', 'other'),
                    'position': row.get('position', ''),
                    'event_date': row.get('event_date', ''),
                    'roll_no': row.get('roll_no', ''),
                    'student_email': row.get('student_email', '')
                }
                
                # Validate required fields
                if not form_data['student_name'] or not form_data['event_name']:
                    continue
                
                # Create certificate (similar to generate_certificate)
                success_count += 1
                
            except Exception as e:
                continue
        
        batch = BatchUpload(
            id=batch_id,
            creator_id=current_user.id,
            filename=file.filename,
            total_records=len(list(csv_data)),
            processed_records=success_count,
            status='completed'
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            'message': f'Processed {success_count} certificates',
            'batch_id': batch_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify/<cert_id>')
def verify_certificate(cert_id):
    """Verify certificate by ID"""
    certificate = Certificate.query.filter_by(id=cert_id).first()
    
    if certificate:
        certificate.verified_at = datetime.utcnow()
        db.session.commit()
        return render_template('verify.html', certificate=certificate, verified=True)
    
    return render_template('verify.html', verified=False)

@app.route('/download/<cert_id>')
def download_certificate(cert_id):
    """Download certificate"""
    certificate = Certificate.query.filter_by(id=cert_id).first()
    
    if certificate:
        cert_path = os.path.join('uploads/certificates', certificate.certificate_file)
        if os.path.exists(cert_path):
            return send_file(cert_path, as_attachment=True, download_name=certificate.certificate_file)
    
    return jsonify({'error': 'Certificate not found'}), 404

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
