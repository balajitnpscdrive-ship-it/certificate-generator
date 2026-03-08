# 🎓 College Certificate Generator

A professional web application for generating personalized certificates for college students participating in sports, cultural, and academic events.

## Features

✨ **Advanced Features:**
- 🖼️ Upload college logo, founder image, principal & secretary signatures
- 📄 Generate individual or batch certificates from CSV
- 🔲 QR code verification for authenticity
- 📧 Email certificates to students
- 🔐 Admin authentication & dashboard
- 📊 Certificate management & tracking
- 🎨 Customizable certificate templates
- 📱 Responsive design

## Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python Flask
- **Database:** SQLite / PostgreSQL
- **PDF/Image:** Pillow, ReportLab, qrcode
- **Email:** Flask-Mail

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual Environment

### Setup

```bash
# Clone repository
git clone https://github.com/balajitnpscdrive-ship-it/certificate-generator.git
cd certificate-generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads/logos uploads/images uploads/signatures uploads/certificates

# Initialize database
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()

# Run application
python app.py
```

Application will be available at `http://localhost:5000`

## Usage

### 1. **Upload Images** (Admin Panel)
- College Logo
- Founder Image
- Principal Signature
- Secretary Signature

### 2. **Create Certificates**
- Enter student details
- Select event
- Generate certificate
- Download as PDF

### 3. **Batch Generate**
- Upload CSV file with student data
- Generate multiple certificates at once

### 4. **Verify Certificates**
- Scan QR code or enter certificate ID
- View certificate details

## CSV Format

For batch certificate generation:

```
student_name,event_name,event_category,position,event_date,rollno
John Doe,Annual Sports Meet,sports,1st Place,2026-03-15,21001
Jane Smith,Cultural Fest,cultural,Participant,2026-03-20,21002
```

## Directory Structure

```
certificate-generator/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── config.py                   # Configuration settings
├── requirements.txt            # Dependencies
├── templates/
│   ├── index.html             # Main dashboard
│   ├── upload_images.html     # Image upload form
│   ├── generate_certificate.html
│   ├── batch_generate.html
│   ├── verify.html
│   └── admin_dashboard.html
├── static/
│   ├── css/
│   │   ├── styles.css
│   │   └── admin.css
│   └── js/
│       ├── script.js
│       └── admin.js
├── uploads/
│   ├── logos/
│   ├── images/
│   ├── signatures/
│   └── certificates/
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/upload-images` | Image upload form |
| POST | `/api/upload-images` | Upload images |
| POST | `/api/generate-certificate` | Generate single certificate |
| POST | `/api/batch-generate` | Batch generate certificates |
| GET | `/verify/<cert_id>` | Verify certificate |
| GET | `/admin` | Admin dashboard |

## License

MIT License - feel free to use for educational purposes.

## Support

For issues or questions, please open an issue on GitHub.

---
Made with ❤️ for educational institutions
