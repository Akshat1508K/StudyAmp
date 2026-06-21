@echo off
echo ============================================================
echo Starting GamuX LMS Backend
echo ============================================================
echo.

cd backend

REM Check if virtual environment exists
if not exist "venv_new\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv_new
    echo Then: venv_new\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv_new\Scripts\activate.bat

REM Start backend
python start_backend.py
