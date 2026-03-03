import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

substring = 'eea9546a'
print(f"--- Searching for substring '{substring}' in all tables ---")

with connection.cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
        columns = cursor.fetchall()
        
        for col, col_type in columns:
            if 'char' in col_type or 'text' in col_type or 'uuid' in col_type or 'json' in col_type:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table}\" WHERE CAST(\"{col}\" AS TEXT) ILIKE '%{substring}%'")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"  FOUND in table '{table}', column '{col}': {count} occurrences")
                except Exception as e:
                    pass

print("\n--- Additional search for d101107a (to verify search logic) ---")
substring2 = 'd101107a'
with connection.cursor() as cursor:
    for table in tables:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
        columns = cursor.fetchall()
        for col, col_type in columns:
            if 'char' in col_type or 'text' in col_type or 'uuid' in col_type or 'json' in col_type:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM \"{table}\" WHERE CAST(\"{col}\" AS TEXT) ILIKE '%{substring2}%'")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"  FOUND in table '{table}', column '{col}': {count} occurrences")
                except Exception as e:
                    pass
