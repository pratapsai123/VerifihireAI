@echo off
echo Starting VerifiHireAI Backend...
cd /d "%~dp0"
call venv\Scripts\activate
python manage.py runserver 8000
pause
