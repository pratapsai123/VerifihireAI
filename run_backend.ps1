# VerifiHire Start Script
echo "Starting VerifiHire Backend & Celery Worker..."

# Start Django Server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\python.exe manage.py runserver 8001"

# Start Celery Worker in the current window
echo "Starting Celery Worker (Pool: Solo)..."
cd backend
.\venv\Scripts\celery.exe -A VerifiHireAI_backend worker --loglevel=info --pool=solo
