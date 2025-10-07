#!/bin/bash

# Database Population Script
echo "🚀 CA Firm Management System - Database Population"
echo "=================================================="

# Activate virtual environment from parent directory
VENV_PATH="../.venv/bin/activate"
if [[ -f "$VENV_PATH" ]]; then
    echo "🔄 Activating virtual environment..."
    source "$VENV_PATH"
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not found at $VENV_PATH"
    echo "   Please ensure the virtual environment is set up correctly"
    echo "   Expected path: /Users/adityabisen/Desktop/CA Updates Agent/CA-Copilot/.venv"
fi

# Check Python version
echo "🐍 Python version: $(python --version 2>/dev/null || echo 'Python not found')"

# Install required packages (bcrypt should already be installed)
echo "📦 Ensuring required packages are installed..."
pip install bcrypt >/dev/null 2>&1

# Run database migrations first
echo "🔄 Running database migrations..."
alembic upgrade head

# Check if migrations were successful
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migration failed. Please check your database configuration."
    exit 1
fi

# Populate database with sample data
echo "🌱 Populating database with sample data..."
python populate_db.py

# Check if population was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database population completed successfully!"
    echo ""
    echo "🔗 You can now start the server with:"
    echo "   uvicorn app.main:app --reload --port 8001"
    echo ""
    echo "📚 API Documentation: http://localhost:8001/docs"
    echo "🔐 Test with Platform Admin: admin@trenor.ai / admin123"
else
    echo "❌ Database population failed. Please check the error messages above."
    exit 1
fi
