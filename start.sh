#!/bin/bash
# VerifiHire Unified Startup Script (Bash/Git Bash)

echo "🚀 Starting VerifiHire AI Suite with broad network access (0.0.0.0)..."

# Start Backend Server
echo "📂 Starting Django Backend..."
(cd backend && ./venv/Scripts/python.exe manage.py runserver 0.0.0.0:8001) &

# Start Celery Worker
echo "⚙️ Starting Celery Worker..."
(cd backend && ./venv/Scripts/celery.exe -A VerifiHireAI_backend worker --loglevel=info --pool=solo) &

# Start Frontend
echo "🎨 Starting React Frontend..."
export HOST=0.0.0.0
(cd frontend && npm start) &

echo "✅ All systems initiated in the background!"
echo "💡 To access from other devices, find your local IP and use http://YOUR_IP:3000"
wait
