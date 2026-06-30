import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'VerifiHireAI_backend.settings'

import django
django.setup()

from django.db import connection
cursor = connection.cursor()

cursor.execute("SELECT name FROM django_migrations WHERE app='api' AND name LIKE '%%0101%%'")
print("Migration 0101 in django_migrations:", cursor.fetchall())

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='api_candidateinvitation' AND column_name='activity_logs'")
r = cursor.fetchall()
print("activity_logs column exists:", bool(r), r)
