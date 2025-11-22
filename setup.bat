@echo off
echo ========================================
echo AI Resume Parser - Setup Script
echo ========================================
echo.

echo [1/5] Setting up backend...
cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Downloading spaCy model...
python -m spacy download en_core_web_sm

echo Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please edit it to set your SECRET_KEY
)

echo.
echo [2/5] Backend setup complete!
echo.

echo [3/5] Creating admin user...
timeout /t 2 /nobreak > nul

echo.
echo [4/5] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Edit backend\.env and set a secure SECRET_KEY
echo.
echo 2. Start the backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python -m uvicorn app.main:app --reload
echo.
echo 3. Start the frontend (in a new terminal):
echo    cd frontend
echo    python -m http.server 8080
echo.
echo 4. Create admin user:
echo    curl -X POST "http://localhost:8000/api/auth/register" ^
echo      -H "Content-Type: application/json" ^
echo      -d "{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\",\"role\":\"admin\"}"
echo.
echo 5. Open http://localhost:8080 in your browser
echo    Login with: admin / admin123
echo.
echo ========================================
echo.

pause
