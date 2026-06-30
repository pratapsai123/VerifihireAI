import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'VerifiHireAI_backend.settings'

import django
django.setup()

from django.db import connection
cursor = connection.cursor()

# Add the missing activity_logs column
cursor.execute("ALTER TABLE api_candidateinvitation ADD COLUMN activity_logs jsonb NOT NULL DEFAULT '[]'::jsonb")
print("activity_logs column added successfully!")

# Verify it exists now
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='api_candidateinvitation' AND column_name='activity_logs'")
r = cursor.fetchall()
print("Verification - activity_logs column exists:", bool(r))
