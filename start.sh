#!/bin/bash

# BPUT Career Platform - One-Click Startup Script
# This script checks dependencies and starts the application

echo "=============================================="
echo "🎓 BPUT Career Platform - Startup Script"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Navigate to backend directory
cd backend || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install/Update dependencies
echo "📦 Installing dependencies..."
pip install --quiet Flask Flask-SQLAlchemy Flask-CORS PyPDF2 python-docx scikit-learn pandas Faker Werkzeug python-dotenv

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    mkdir uploads
    echo "✅ Created uploads directory"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOL
SECRET_KEY=bput-career-demo-secret-key-2025
DATABASE_URL=sqlite:///bput_career_demo.db
FLASK_ENV=development
EOL
    echo "✅ .env file created"
fi
echo ""

# Start the backend server
echo "=============================================="
echo "🚀 Starting BPUT Career Platform Backend..."
echo "=============================================="
echo ""
echo "Backend will run at: http://localhost:5000"
echo "API Documentation: http://localhost:5000/api"
echo ""
echo "Demo Accounts:"
echo "  👨‍🎓 Student: student@bput.ac.in / demo123"
echo "  🏢 Employer: employer@company.com / demo123"
echo "  👨‍💼 Admin: admin@bput.ac.in / admin123"
echo ""
echo "Press CTRL+C to stop the server"
echo "=============================================="
echo ""

# Run the Flask app
python app.py