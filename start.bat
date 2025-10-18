@echo off
REM BPUT Career Platform - Windows Startup Script

echo ==============================================
echo 🎓 BPUT Career Platform - Startup Script
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Navigate to backend directory
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install --quiet Flask Flask-SQLAlchemy Flask-CORS PyPDF2 python-docx scikit-learn pandas Faker Werkzeug python-dotenv

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Create uploads directory
if not exist "uploads" (
    mkdir uploads
    echo ✅ Created uploads directory
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    (
        echo SECRET_KEY=bput-career-demo-secret-key-2025
        echo DATABASE_URL=sqlite:///bput_career_demo.db
        echo FLASK_ENV=development
    ) > .env
    echo ✅ .env file created
)
echo.

REM Start the backend server
echo ==============================================
echo 🚀 Starting BPUT Career Platform Backend...
echo ==============================================
echo.
echo Backend will run at: http://localhost:5000
echo API Documentation: http://localhost:5000/api
echo.
echo Demo Accounts:
echo   👨‍🎓 Student: student@bput.ac.in / demo123
echo   🏢 Employer: employer@company.com / demo123
echo   👨‍💼 Admin: admin@bput.ac.in / admin123
echo.
echo Press CTRL+C to stop the server
echo ==============================================
echo.

REM Run the Flask app
python app.py

pause