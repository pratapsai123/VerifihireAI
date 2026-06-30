# All-in-one startup script for VerifiHireAI (Windows PowerShell)

# 1. Create Python venv if not exists
if (-not (Test-Path "backend\venv")) {
    python -m venv backend\venv
}

# 2. Activate venv and install backend dependencies
& backend\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend\requirements.txt

# 3. Install frontend dependencies
cd frontend
npm install
cd ..

# 4. Run Django migrations
cd backend
& venv\Scripts\Activate.ps1
python manage.py migrate

# 5. Start backend server (runs in background)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; & venv\Scripts\Activate.ps1; python manage.py runserver"

# 6. Start Celery worker (runs in background)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; & venv\Scripts\Activate.ps1; celery -A VerifiHireAI_backend worker --loglevel=info"

cd ..

# 7. Start frontend (runs in background)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

# 8. Start DeepFace service (runs in background)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd deepface; & ..\backend\venv\Scripts\Activate.ps1; python run.py"

Write-Host "All services started in separate terminals."
