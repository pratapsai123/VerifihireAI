import os
import sys
import django

sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

def check():
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'api_contactsubmission'")
        table_exists = cursor.fetchone()[0] > 0
        print(f"Table api_contactsubmission exists: {table_exists}")
        
        cursor.execute("SELECT count(*) FROM information_schema.columns WHERE table_name = 'api_assessment' AND column_name = 'assessment_mode'")
        column_exists = cursor.fetchone()[0] > 0
        print(f"Column assessment_mode in api_assessment exists: {column_exists}")

if __name__ == "__main__":
    check()
