@echo off
echo ==========================================
echo Setting up VerifiHireAI Frontend...
echo ==========================================

cd frontend

if not exist node_modules (
    echo Installing Node modules... this may take a few minutes...
    call npm install
)

echo ==========================================
echo Starting React App on Port 3000...
echo ==========================================
call npm start
pause
