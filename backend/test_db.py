import os
import psycopg2

try:
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'verifihire_db'),
        user=os.environ.get('POSTGRES_USER', 'verifihire_user'),
        password=os.environ.get('POSTGRES_PASSWORD', 'verifihire_password'),
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=os.environ.get('POSTGRES_PORT', '5432')
    )
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
