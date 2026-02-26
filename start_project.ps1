# VerifiHire Unified Startup Script (Windows PowerShell)
# This script starts the Frontend, Backend, and Celery worker in separate windows.

Write-Host "🚀 Starting VerifiHire AI Suite with broad network access (0.0.0.0)..." -ForegroundColor Cyan

# 1. Start Redis check (optional - assumes it's running as a service or Docker)
Write-Host "📡 Ensure Redis is running on port 6379..."

# 2. Start Backend Server (Port 8001) - Binding to 0.0.0.0
Write-Host "📂 Starting Django Backend on port 8001 (Listening on 0.0.0.0)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8001"

# 3. Start Celery Worker (Background Tasks)
Write-Host "⚙️ Starting Celery Worker (Pool: Solo)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\celery.exe -A VerifiHireAI_backend worker --loglevel=info --pool=solo"

# 4. Start Frontend (Port 3000) - Set HOST to 0.0.0.0
Write-Host "🎨 Starting React Frontend on port 3000 (Listening on 0.0.0.0)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; `$env:HOST='0.0.0.0'; npm start"

Write-Host "✅ All systems initiated! Check the separate windows for status." -ForegroundColor Green
Write-Host "💡 To access from other devices, find your local IP (run 'ipconfig') and use http://YOUR_IP:3000" -ForegroundColor Cyan
