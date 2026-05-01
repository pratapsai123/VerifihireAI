#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

# Get all migration files
migration_dir = os.path.join(os.path.dirname(__file__), 'api', 'migrations')
existing_migrations = []

for f in sorted(os.listdir(migration_dir)):
    if f.endswith('.py') and f != '__init__.py':
        name = f.replace('.py', '')
        existing_migrations.append(name)

print(f"Found {len(existing_migrations)} migration files")

with connection.cursor() as cursor:
    # Check which migrations are already in the table
    cursor.execute("SELECT name FROM django_migrations WHERE app = 'api'")
    applied = set([r[0] for r in cursor.fetchall()])
    print(f"Already applied: {len(applied)}")
    
    # Add missing ones
    for name in existing_migrations:
        if name not in applied:
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                ['api', name]
            )
            print(f"Faked: {name}")
    
print("Done!")
