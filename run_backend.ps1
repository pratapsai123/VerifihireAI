# VerifiHire Start Script
Write-Output "Starting VerifiHire Backend & Celery Worker..."

# Start Django Server in a new window - Binding to 0.0.0.0
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location backend; .\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8001"

# Start Celery Worker in the current window
Write-Output "Starting Celery Worker (Pool: Solo)..."
Set-Location backend
.\venv\Scripts\celery.exe -A VerifiHireAI_backend worker --loglevel=info --pool=solo
