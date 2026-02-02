#!/bin/bash
# Face Verification API - Production Startup Script
# Version: 2.1.0

echo "========================================"
echo "Face Verification API v2.1.0"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    echo "Then: source venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "[1/3] Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "[2/3] Checking dependencies..."
python -c "import fastapi, insightface, cv2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
mkdir -p cropped
mkdir -p manual_review

# Start the server
echo "[3/3] Starting Face Verification API..."
echo ""
echo "Server will start at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
