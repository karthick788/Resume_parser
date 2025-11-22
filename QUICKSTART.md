# 🚀 Quick Start Guide - AI Resume Parser

## Prerequisites
- Python 3.8+ installed
- Modern web browser

## Installation (5 minutes)

### Option 1: Automated Setup (Windows)

```bash
# Run the setup script
setup.bat
```

### Option 2: Manual Setup

**1. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env file
copy .env.example .env
```

**2. Edit .env file**
- Open `backend/.env`
- Change `SECRET_KEY` to a random string

**3. Start Backend**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

✅ Backend running at: http://localhost:8000

**4. Start Frontend** (new terminal)
```bash
cd frontend
python -m http.server 8080
```

✅ Frontend running at: http://localhost:8080

## First Time Setup

**Create Admin User**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\",\"role\":\"admin\"}"
```

## Usage

1. **Open Browser**: http://localhost:8080
2. **Login**: username: `admin`, password: `admin123`
3. **Upload Resume**: Go to "Upload Resume" page
4. **Drag & Drop**: Drop a PDF or DOCX file
5. **Parse**: Click "Upload & Parse"
6. **View Results**: See extracted information

## API Documentation

Swagger UI: http://localhost:8000/docs

## Troubleshooting

**spaCy model not found?**
```bash
python -m spacy download en_core_web_sm
```

**Port 8000 already in use?**
```bash
uvicorn app.main:app --port 8001
```

**CORS errors?**
- Check frontend URL is in `backend/.env` CORS_ORIGINS

## What's Next?

- Upload test resumes
- Explore the dashboard
- Try candidate search
- Export data to CSV/JSON
- Check analytics

## Support

See [README.md](README.md) for detailed documentation.
