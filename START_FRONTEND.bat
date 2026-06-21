@echo off
echo ============================================================
echo Starting GamuX LMS Frontend
echo ============================================================
echo.

cd frontend-react

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
)

REM Start frontend
echo.
echo Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo.
call npm start
