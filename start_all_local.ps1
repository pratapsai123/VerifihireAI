# VerifiHire AI - Unified Local Startup Script (Windows PowerShell)
# This script starts everything needed for local development.

Write-Host "🚀 Starting VerifiHire AI Suite (Local Mode)..." -ForegroundColor Cyan

# 0. Ensure Local Configuration
Write-Host "🔧 Converting configuration to Localhost..." -ForegroundColor Yellow
python convert_to_local.py

# 1. Start Docker Dependencies (Redis, Nginx, Executor, DinD)
Write-Host "📡 Starting Docker dependencies..." -ForegroundColor Yellow
cd "$PSScriptRoot"
docker-compose up -d redis nginx executor dind certbot

# 2. Start Backend Server (Port 8001)
Write-Host "📂 Starting Django Backend on port 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (Test-Path 'venv') { .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8001 } else { python manage.py runserver 0.0.0.0:8001 }"

# 3. Start Celery Worker
Write-Host "⚙️ Starting Celery Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (Test-Path 'venv') { .\venv\Scripts\celery.exe -A VerifiHireAI_backend worker --loglevel=info --pool=solo } else { celery -A VerifiHireAI_backend worker --loglevel=info --pool=solo }"

# 4. Start Main Frontend (Port 3000)
Write-Host "🎨 Starting Main Frontend on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; `$env:PORT=3000; npm start"

# 5. Start Admin Portal (Port 3001)
Write-Host "🛠️ Starting Admin Portal on port 3001..." -ForegroundColor Yellow
# Path to admin is relative to VerifiHireAI folder: ../verifihire-admin/VerifiHireAI
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ../verifihire-admin/VerifiHireAI; npm run dev"

Write-Host ""
Write-Host "✅ All systems initiated!" -ForegroundColor Green
Write-Host "🔗 Main Portal:  https://verifihireai.com (via Nginx) or http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔗 Admin Portal: https://verifihireai.com/admin (via Nginx) or http://localhost:3001/admin/" -ForegroundColor Cyan
Write-Host "🔗 Backend API:  http://localhost:8001/api/" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Note: Ensure your local PostgreSQL is running on port 5432." -ForegroundColor Red
