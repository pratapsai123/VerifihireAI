import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

def check_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Columns for {table_name}:")
        for col in columns:
            print(f"  - {col}")
        if 'company_id' in columns:
            print(f"SUCCESS: {table_name} has company_id")
        else:
            print(f"FAILURE: {table_name} missing company_id")

print("Checking database columns...")
check_table('ai_assessment')
check_table('ai_candidate')
