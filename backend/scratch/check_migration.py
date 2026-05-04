import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'VerifiHireAI_backend.settings'
django.setup()
from django.db import connection

cursor = connection.cursor()

# Check if migration 0101 is recorded as applied
cursor.execute("SELECT name FROM django_migrations WHERE app='api' AND name LIKE '%%0101%%'")
print("Migration 0101 in django_migrations:", cursor.fetchall())

# Check if activity_logs column actually exists
cursor.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name='api_candidateinvitation' AND column_name='activity_logs'
""")
result = cursor.fetchall()
print("activity_logs column exists:", bool(result), result)
