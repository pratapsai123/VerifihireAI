# How to Start Fresh with react_user Database

## The Issue
When you renamed the database in `settings.py` from `resct_test` to `react_user`, Django only changed which database to connect to. It doesn't automatically create a new empty database.

## Why You Could Still Login
- **If running locally**: The `react_user` database is empty (0 users), so login should fail
- **If running in Docker**: Docker was using `verifihireai` database (from docker-compose.yml), which still had your old data

## Solution: Start Fresh

### Option 1: Reset Docker Database (Recommended if using Docker)

1. **Stop all containers:**
   ```bash
   docker-compose down
   ```

2. **Remove the database volume (THIS DELETES ALL DATA):**
   ```bash
   docker volume rm verifihireai_pgdata
   ```

3. **Start fresh:**
   ```bash
   docker-compose up -d db
   ```

4. **Run migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Start all services:**
   ```bash
   docker-compose up -d
   ```

### Option 2: Reset Local Database (If running locally)

1. **Connect to PostgreSQL and drop/create database:**
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres -h localhost
   
   -- Drop the database
   DROP DATABASE IF EXISTS react_user;
   
   -- Create new empty database
   CREATE DATABASE react_user;
   
   -- Exit
   \q
   ```

2. **Run migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

3. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

## Verify Fresh Start

After resetting, check that the database is empty:
```bash
cd backend
python check_db.py
```

You should see:
- UserProfile records: 0
- Auth User records: 0
- ApplicationAdmin records: 0

Now you'll need to register a new user to login!

