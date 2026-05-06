import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app = 'api' ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print("Last 5 'api' migrations:")
    for row in rows:
        print(row)

    cursor.execute("SELECT name FROM django_migrations WHERE app = 'api' AND name = '0101_contactsubmission_assessment_assessment_mode_and_more'")
    if cursor.fetchone():
        print("\n0101 is IN the database.")
    else:
        print("\n0101 is NOT in the database.")

    cursor.execute("SELECT name FROM django_migrations WHERE app = 'api' AND name = '0100_merge_20260505_1042'")
    if cursor.fetchone():
        print("0100 is IN the database.")
    else:
        print("0100 is NOT in the database.")
