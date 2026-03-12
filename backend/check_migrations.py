import os
import django
from django.db.migrations.recorder import MigrationRecorder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

with open('migration_status.txt', 'w') as f:
    for app in ['ai_assessments', 'ai_candidates']:
        f.write(f"\nApplied migrations for {app}:\n")
        applied = MigrationRecorder.Migration.objects.filter(app=app).values_list('name', flat=True)
        for m in sorted(applied):
            f.write(f"  - {m}\n")
