import os
import django
from django.db.migrations.recorder import MigrationRecorder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

with open('migration_status.log', 'w') as f:
    applied = MigrationRecorder.Migration.objects.filter(app='ai_assessments').values_list('name', flat=True)
    f.write("Applied migrations for ai_assessments:\n")
    for m in sorted(applied):
        f.write(f"[X] {m}\n")

    migration_dir = os.path.join('ai_assessments', 'migrations')
    all_migrations = os.listdir(migration_dir)
    f.write("\nAll migration files in ai_assessments/migrations:\n")
    for m in sorted(all_migrations):
        if m.endswith('.py') and m != '__init__.py':
            is_applied = m.replace('.py', '') in applied
            status = "[X]" if is_applied else "[ ]"
            f.write(f"{status} {m}\n")

    # Repeat for ai_candidates
    applied_c = MigrationRecorder.Migration.objects.filter(app='ai_candidates').values_list('name', flat=True)
    f.write("\nApplied migrations for ai_candidates:\n")
    for m in sorted(applied_c):
        f.write(f"[X] {m}\n")

    migration_dir_c = os.path.join('ai_candidates', 'migrations')
    all_migrations_c = os.listdir(migration_dir_c)
    f.write("\nAll migration files in ai_candidates/migrations:\n")
    for m in sorted(all_migrations_c):
        if m.endswith('.py') and m != '__init__.py':
            is_applied = m.replace('.py', '') in applied_c
            status = "[X]" if is_applied else "[ ]"
            f.write(f"{status} {m}\n")
