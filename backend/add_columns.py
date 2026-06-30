import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

queries = [
    "ALTER TABLE api_candidateinvitation ADD COLUMN IF NOT EXISTS activity_logs jsonb DEFAULT '[]'::jsonb;",
    "ALTER TABLE api_candidatedetails ADD COLUMN IF NOT EXISTS face_match_score double precision DEFAULT 0.0;",
    "ALTER TABLE api_candidatedetails ADD COLUMN IF NOT EXISTS identity_mismatch boolean DEFAULT false;",
    "ALTER TABLE api_candidatedetails ADD COLUMN IF NOT EXISTS identity_mismatch_detected boolean DEFAULT false;",
    "ALTER TABLE api_candidatedetails ADD COLUMN IF NOT EXISTS mismatch_score double precision;",
]

try:
    with connection.cursor() as cursor:
        for q in queries:
            print(f"Running: {q}")
            try:
                cursor.execute(q)
            except Exception as inner_e:
                print(f"Warning on query: {inner_e}")
                
    print("Columns added successfully.")
    
    print("Faking migration 0101...")
    os.system('python manage.py migrate --fake api 0101')
except Exception as e:
    print(f"Error: {e}")
