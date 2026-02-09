# VerifiHireAI

VeriFiHireAI is a comprehensive hiring assessment platform with Django backend and React frontend.

## Docker Setup

Run the full stack (Django backend, React frontend, and Postgres) with Docker.

### Prerequisites
- Docker and Docker Compose installed.

### Quick Start
```bash
# From the repo root
docker-compose build
docker-compose up -d
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000/api  
- Postgres: exposed only inside the Compose network.

Logs (tail): `docker-compose logs -f backend frontend db`  
Stop: `docker-compose down`

## Configurable Environment
Adjust values in `docker-compose.yml` as needed:
- Backend env: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`
- Database: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- CORS/CSRF: `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`
- Frontend build arg: `REACT_APP_API_BASE_URL` (default points to `http://backend:8000/api`)

Migrations run automatically on container start.
