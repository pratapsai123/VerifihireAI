import os
import django
from django.db.migrations.recorder import MigrationRecorder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

with open('migration_diagnostics.txt', 'w', encoding='utf-8') as f:
    for app in ['ai_assessments', 'ai_candidates']:
        f.write(f"\n--- App: {app} ---\n")
        applied = set(MigrationRecorder.Migration.objects.filter(app=app).values_list('name', flat=True))
        
        migration_dir = os.path.join(app, 'migrations')
        if not os.path.exists(migration_dir):
            f.write(f"Migration dir {migration_dir} not found!\n")
            continue
            
        files = [m for m in os.listdir(migration_dir) if m.endswith('.py') and m != '__init__.py']
        for m in sorted(files):
            name = m.replace('.py', '')
            status = "[X]" if name in applied else "[ ]"
            f.write(f"{status} {m}\n")
            
        unaccounted = applied - {m.replace('.py', '') for m in files}
        if unaccounted:
            f.write("\nApplied but missing file:\n")
            for u in sorted(unaccounted):
                f.write(f"[!] {u}\n")
