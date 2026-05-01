#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Delete the problematic migration record
    cursor.execute("DELETE FROM django_migrations WHERE app = 'api' AND name = '0106_merge_20260429_1511'")
    print('Cleaned up migration history')
    # Show remaining api migrations
    cursor.execute("SELECT name FROM django_migrations WHERE app = 'api' ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    print('Recent api migrations:', [r[0] for r in rows])
