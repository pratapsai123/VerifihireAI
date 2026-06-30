import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # 1. Rename existing table
        print("Renaming table to backup...")
        cursor.execute('ALTER TABLE api_contactsubmission RENAME TO api_contactsubmission_backup;')
        
    # 2. Run migration
    print("Running migration...")
    exit_code = os.system('python manage.py migrate api 0101')
    
    if exit_code == 0:
        with connection.cursor() as cursor:
            # 3. Copy data back
            print("Restoring data...")
            cursor.execute('''
                INSERT INTO api_contactsubmission (id, full_name, email, company, subject, message, created_at)
                SELECT id, full_name, email, company, subject, message, created_at
                FROM api_contactsubmission_backup;
            ''')
            # 4. Update sequence so future inserts work properly
            cursor.execute("SELECT setval('api_contactsubmission_id_seq', (SELECT MAX(id) FROM api_contactsubmission));")
            # 5. Drop backup
            cursor.execute('DROP TABLE api_contactsubmission_backup;')
            print("Success!")
    else:
        print("Migration failed, restoring table name...")
        with connection.cursor() as cursor:
            cursor.execute('ALTER TABLE api_contactsubmission_backup RENAME TO api_contactsubmission;')
            
except Exception as e:
    print(f"Error: {e}")
