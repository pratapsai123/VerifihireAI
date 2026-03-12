import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

def check_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
        columns = [row[0] for row in cursor.fetchall()]
        res = f"Columns for {table_name}:\n"
        for col in columns:
            res += f"  - {col}\n"
        if 'company_id' in columns:
            res += f"SUCCESS: {table_name} has company_id\n"
        else:
            res += f"FAILURE: {table_name} missing company_id\n"
    return res

with open('verify_db_out.txt', 'w', encoding='utf-8') as f:
    f.write("Checking database columns...\n")
    f.write(check_table('ai_assessment'))
    f.write(check_table('ai_candidate'))
