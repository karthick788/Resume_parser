# 🤖 AI Resume Parser & Screening System

A complete, production-ready AI-powered resume parsing and candidate screening system built with Machine Learning and Natural Language Processing.

## 📋 Overview

This system automatically extracts structured information from resumes (PDF/DOCX), uses ML-based Named Entity Recognition for intelligent parsing, scores candidates, and provides a modern web interface for managing and analyzing parsed data.

### Key Features

- ✅ **Intelligent Resume Parsing** - Extract text from PDF and DOCX files
- 🧠 **ML-Based Entity Extraction** - spaCy NER for identifying names, emails, skills, etc.
- 📊 **Candidate Scoring** - Automated scoring based on experience, skills, education
- 🔍 **Advanced Search** - Filter candidates by skills, experience, keywords
- 📈 **Analytics Dashboard** - Visualize parsing trends and skill distributions
- 💾 **Data Export** - Export candidate data in JSON/CSV formats
- 🔐 **Secure Authentication** - JWT-based user authentication
- 🎨 **Modern UI** - Clean, responsive web interface

## 🏗️ Architecture

```
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── models/   # Database models
│   │   ├── routes/   # API endpoints
│   │   ├── services/ # Business logic (NLP, ML, Scoring)
│   │   └── utils/    # Utilities
│   └── requirements.txt
│
└── frontend/         # HTML/CSS/JS frontend
    ├── css/
    ├── js/
    └── *.html
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Modern web browser

### Installation

**1. Clone the repository**
```bash
cd ResumeParser
```

**2. Set up Backend**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure environment
copy .env.example .env
# Edit .env and set SECRET_KEY

# Run backend
python -m uvicorn app.main:app --reload
```

Backend will run at: `http://localhost:8000`

**3. Set up Frontend**

```bash
cd ../frontend

# Open with Live Server or any HTTP server
# For Python's built-in server:
python -m http.server 8080
```

Frontend will run at: `http://localhost:8080`

**4. Create Admin User**

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"admin123","role":"admin"}'
```

**5. Login**

- Open `http://localhost:8080` in your browser
- Login with: `admin` / `admin123`

## 📖 Usage Guide

### 1. Upload Resume

- Navigate to "Upload Resume" page
- Drag & drop or click to select PDF/DOCX file
- Click "Upload & Parse"
- System will automatically extract and parse information

### 2. View Candidates

- Go to "Candidates" page
- Browse all parsed candidates
- Click on a candidate to view detailed information
- Export candidate data as JSON or CSV

### 3. Search & Filter

- Use the search functionality to find candidates by:
  - Skills
  - Experience level
  - Keywords in name/email/summary

### 4. Analytics

- View dashboard metrics:
  - Total resumes processed
  - Success rate
  - Average experience
  - Skills distribution
  - Parsing trends

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **spaCy** - NLP and Named Entity Recognition
- **pdfplumber** - PDF text extraction
- **python-docx** - DOCX parsing
- **scikit-learn** - ML utilities and TF-IDF
- **JWT** - Authentication

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript (ES6+)** - Client-side logic
- **Fetch API** - HTTP requests

### Database
- **SQLite** - Development database (easily switchable to PostgreSQL)

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Main Endpoints

**Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

**Resumes**
- `POST /api/resumes/upload` - Upload resume file
- `GET /api/resumes` - List all resumes
- `POST /api/resumes/{id}/parse` - Parse resume
- `DELETE /api/resumes/{id}` - Delete resume

**Candidates**
- `GET /api/candidates` - List candidates
- `GET /api/candidates/{id}` - Get candidate details
- `POST /api/candidates/search` - Search candidates
- `GET /api/candidates/{id}/export` - Export data

**Analytics**
- `GET /api/analytics/overview` - Dashboard metrics
- `GET /api/analytics/skills-distribution` - Top skills
- `GET /api/analytics/trends` - Parsing trends

## 🧪 Testing

### Test with Sample Resume

1. Create a sample resume (PDF or DOCX)
2. Upload through the UI
3. Click "Parse" to extract information
4. View extracted data in candidate details

### API Testing

```bash
# Get auth token
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Upload resume
curl -X POST "http://localhost:8000/api/resumes/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_resume.pdf"

# List candidates
curl -X GET "http://localhost:8000/api/candidates" \
  -H "Authorization: Bearer $TOKEN"
```

## 📁 Project Structure

```
ResumeParser/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── candidate.py
│   │   │   └── job.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   ├── candidate.py
│   │   │   └── analytics.py
│   │   ├── services/
│   │   │   ├── text_extraction.py
│   │   │   ├── nlp_pipeline.py
│   │   │   ├── ml_parser.py
│   │   │   ├── scoring.py
│   │   │   └── job_matching.py
│   │   ├── utils/
│   │   │   ├── regex_patterns.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── uploads/
│   ├── models/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── dashboard.js
│   │   └── upload.js
│   ├── index.html
│   ├── dashboard.html
│   └── upload.html
├── PROJECT_OVERVIEW.md
└── README.md
```

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- File upload validation
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration

## 🎯 Scoring Algorithm

Candidates are scored based on:
- **Experience** (30%) - Years of relevant experience
- **Skills** (35%) - Match with required/preferred skills
- **Education** (20%) - Degree level and institution
- **Certifications** (10%) - Professional certifications
- **Projects** (5%) - Portfolio projects

Score ranges:
- 90-100: A+ (Excellent)
- 80-89: A (Very Good)
- 70-79: B (Good)
- 60-69: C (Fair)
- Below 60: D (Needs Improvement)

## 📈 Future Enhancements

- [ ] Multi-language support
- [ ] BERT-based NER model
- [ ] OCR for scanned PDFs
- [ ] Job recommendation engine
- [ ] Email integration
- [ ] Batch processing
- [ ] Advanced analytics
- [ ] Mobile app

## 🐛 Troubleshooting

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**Database errors:**
Delete `resume_parser.db` and restart the backend.

**CORS errors:**
Check that frontend URL is in `CORS_ORIGINS` in `.env`

**Port already in use:**
Change port in `.env` or run with different port:
```bash
uvicorn app.main:app --port 8001
```

## 📝 License

This project is for educational and portfolio purposes.

## 👨‍💻 Author

Created as part of the AI Resume Parser & Screening System project.

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- FastAPI for the excellent web framework
- pdfplumber for PDF extraction
- All open-source contributors

---

**For detailed technical documentation, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**
