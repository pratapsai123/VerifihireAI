from api.models import InterviewSlot
from datetime import datetime, timedelta
import datetime as dt

def run():
    slots = InterviewSlot.objects.filter(status='available')
    count = 0
    for s in slots:
        d1 = dt.datetime.combine(dt.date.today(), s.start_time)
        d2 = dt.datetime.combine(dt.date.today(), s.end_time)
        if (d2 - d1) != timedelta(minutes=50):
            print(f"Deleting stale available slot {s.id}: {s.start_time}-{s.end_time}")
            s.delete()
            count += 1
    print(f"Deleted {count} stale available slots.")

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
    django.setup()
    run()
