# AI Resume Parser - Backend

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

For better accuracy (larger model):
```bash
python -m spacy download en_core_web_lg
```

### 5. Configure Environment

Copy `.env.example` to `.env` and update settings:

```bash
copy .env.example .env
```

Edit `.env` and change:
- `SECRET_KEY` to a secure random string
- Other settings as needed

### 6. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

Or:

```bash
cd app
python main.py
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info

### Resumes
- `POST /api/resumes/upload` - Upload resume file
- `GET /api/resumes` - List all resumes
- `GET /api/resumes/{id}` - Get resume details
- `POST /api/resumes/{id}/parse` - Parse resume
- `DELETE /api/resumes/{id}` - Delete resume

### Candidates
- `GET /api/candidates` - List candidates
- `GET /api/candidates/{id}` - Get candidate details
- `PUT /api/candidates/{id}` - Update candidate
- `DELETE /api/candidates/{id}` - Delete candidate
- `POST /api/candidates/search` - Search candidates
- `GET /api/candidates/{id}/export` - Export candidate data

### Analytics
- `GET /api/analytics/overview` - Dashboard metrics
- `GET /api/analytics/skills-distribution` - Top skills
- `GET /api/analytics/trends` - Parsing trends

## Project Structure

```
backend/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI app
├── uploads/             # Uploaded files
├── models/              # ML models
├── requirements.txt     # Dependencies
└── .env                 # Environment variables
```

## Testing

Create a test user:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"admin123","role":"admin"}'
```

Login:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

## Development

- FastAPI auto-generates API docs at `/docs`
- Database is SQLite by default (resume_parser.db)
- File uploads stored in `./uploads/`
- ML model cached in memory after first load

## Troubleshooting

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**Database errors:**
Delete `resume_parser.db` and restart the app to recreate tables.

**Port already in use:**
Change port in `.env` or run with:
```bash
uvicorn app.main:app --port 8001
```
