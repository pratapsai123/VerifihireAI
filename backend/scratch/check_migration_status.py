import os
import sys
import django

sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

def check():
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM django_migrations WHERE app = 'api' AND name = '0101_contactsubmission_assessment_assessment_mode'")
        applied = cursor.fetchone()[0] > 0
        print(f"Migration 0101 applied: {applied}")

if __name__ == "__main__":
    check()
