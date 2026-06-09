# PowerShell script to reset Django database
# Run from the backend directory

Write-Host "Resetting Django Database..." -ForegroundColor Green

# Option 1: Delete SQLite database (if using SQLite)
# Remove-Item db.sqlite3 -ErrorAction SilentlyContinue

# Option 2: For PostgreSQL - recreate database (adjust credentials)
# psql -U postgres -c "DROP DATABASE IF EXISTS verifihireai;"
# psql -U postgres -c "CREATE DATABASE verifihireai;"

# Remove all migration files except __init__.py
Get-ChildItem -Path "api\migrations" -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item
Get-ChildItem -Path "ai_assessments\migrations" -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item
Get-ChildItem -Path "ai_candidates\migrations" -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item

# Remove __pycache__ folders
Get-ChildItem -Path "api\migrations" -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force

# Create fresh migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
Write-Host "Database reset complete!" -ForegroundColor Green
Write-Host "Run 'python manage.py createsuperuser' if you need an admin account."
