# VerifiHireAI Project

## Project Structure
- `frontend/` — React app (port 3000)
- `backend/` — Django REST API (port 8001)

## Tech Stack
- **Frontend**: React, Axios, lucide-react, recharts
- **Backend**: Django + DRF, PostgreSQL, Celery, Redis
- **Auth**: JWT tokens (`authToken` in localStorage)

## Database
- DB: `verifihire_db`
- User: `postgres` / Password: `root`
- Host: `127.0.0.1:5432`

## Running the Project
```bash
# Backend
cd backend
.\venv\Scripts\activate
python manage.py runserver 0.0.0.0:8001

# Frontend
cd frontend
npm start

# Celery worker
celery -A VerifiHireAI_backend worker --loglevel=info
```

## Key Models
- `JobRole` — table: `api_jobroles` (title, description, created_at, updated_at)
- Candidates, Assessments, Interviews, Results

## Active Branch
- `indu` (main development branch)

## API Base URL
- `http://localhost:8001/api/`

## Important Notes
- Always use `verifihire_user` for prod, `postgres/root` for local dev
- JWT token must be in localStorage as `authToken`
- Migrations folder: `backend/api/migrations/`
