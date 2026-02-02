@echo off
REM Face Verification API - Production Startup Script
REM Version: 2.1.0

echo ========================================
echo Face Verification API v2.1.0
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [2/3] Checking dependencies...
python -c "import fastapi, insightface, cv2" 2>nul
if errorlevel 1 (
    echo [WARNING] Dependencies not installed!
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Create necessary directories
if not exist "cropped\" mkdir cropped
if not exist "manual_review\" mkdir manual_review

REM Start the server
echo [3/3] Starting Face Verification API...
echo.
echo Server will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

pause
