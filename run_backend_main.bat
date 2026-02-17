@echo off
echo ==========================================
echo Setting up VerifiHireAI Backend...
echo ==========================================

cd backend

if not exist venv\Scripts\activate (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Upgrading pip...
    python -m pip install --upgrade pip
) else (
    call venv\Scripts\activate
)

echo Installing dependencies...
call pip install --no-input --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
call pip install --no-input -r requirements.txt

echo Running migrations...
python manage.py migrate

echo ==========================================
echo Starting Django Server on Port 8000...
echo ==========================================
python manage.py runserver 8000
pause
