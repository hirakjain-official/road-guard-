@echo off
echo ============================
echo  Road Guard — Setup
echo ============================
echo.
echo [1/2] Installing Python backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python is in PATH.
    pause
    exit /b 1
)
cd ..

echo.
echo [2/2] Installing frontend dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo ERROR: npm install failed. Make sure Node.js is in PATH.
    pause
    exit /b 1
)
cd ..

echo.
echo ============================
echo  Setup complete!
echo  Copy backend\.env.example to backend\.env
echo  and fill in your Vapi credentials.
echo  Then run: start.bat
echo ============================
pause
