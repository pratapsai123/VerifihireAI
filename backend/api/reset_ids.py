import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

def reset_table():
    with connection.cursor() as cursor:
        print("Truncating table and resetting identity...")
        cursor.execute("TRUNCATE TABLE api_question RESTART IDENTITY CASCADE;")
        print("Successfully reset api_question table.")

if __name__ == "__main__":
    reset_table()
