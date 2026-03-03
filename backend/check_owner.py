import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name, table_schema, table_type
        FROM information_schema.tables 
        WHERE table_name = 'api_jobrole';
    """)
    res = cursor.fetchall()
    print("Search for api_jobrole:")
    for r in res:
        print(f" - Table: {r[0]}, Schema: {r[1]}, Type: {r[2]}")

    cursor.execute("SELECT table_name, table_owner FROM pg_catalog.pg_tables WHERE tablename = 'api_jobrole';")
    owners = cursor.fetchall()
    print("\nOwners (pg_tables):")
    for o in owners:
        print(f" - Table: {o[0]}, Owner: {o[1]}")
