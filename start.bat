@echo off
echo ============================
echo  Road Guard — Starting
echo ============================
echo.
echo Starting backend on http://localhost:8000 ...
start "Road Guard Backend" cmd /k "cd /d %~dp0backend && python main.py"

timeout /t 3 /nobreak >nul

echo Starting frontend on http://localhost:5173 ...
start "Road Guard Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 2 /nobreak >nul
echo.
echo Open http://localhost:5173 in your browser
echo.
