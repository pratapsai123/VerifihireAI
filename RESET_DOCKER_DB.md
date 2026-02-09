# Reset Docker Database to react_user

## Steps to Reset Database

1. **Stop all containers:**
   ```bash
   docker-compose down
   ```

2. **Remove the database volume (THIS DELETES ALL DATA):**
   ```bash
   docker volume rm verifihireai_pgdata
   ```

3. **Start the database service:**
   ```bash
   docker-compose up -d db
   ```

4. **Wait a few seconds for database to initialize, then run migrations:**
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

## Verify Database Name

After starting, verify the database name:
```bash
docker-compose exec backend python manage.py shell -c "from django.conf import settings; print('DB_NAME:', settings.DATABASES['default']['NAME'])"
```

Should output: `DB_NAME: react_user`

## After Reset

- All data will be deleted
- You'll need to register a new user
- You'll need to create coding questions again
- All assessments will be gone

