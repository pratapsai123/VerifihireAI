#!/bin/bash
# VerifiHire Unified Startup Script (Bash/Git Bash)

echo "🚀 Starting VerifiHire AI Suite..."

# Start Backend Server
echo "📂 Starting Django Backend..."
(cd backend && ./venv/Scripts/python.exe manage.py runserver 8001) &

# Start Celery Worker
echo "⚙️ Starting Celery Worker..."
(cd backend && ./venv/Scripts/celery.exe -A VerifiHireAI_backend worker --loglevel=info --pool=solo) &

# Start Frontend
echo "🎨 Starting React Frontend..."
(cd frontend && npm start) &

echo "✅ All systems initiated in the background!"
wait
