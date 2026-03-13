import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import ApplicationAdmin
from django.contrib.auth.models import User

admin = ApplicationAdmin.objects.first()
if admin:
    print(f"Application Admin User: {admin.user.username}, Email: {admin.user.email}")
else:
    print("No Application Admin record found!")

# Also list all users for context
print("\nAll Users:")
for user in User.objects.all():
    print(f"Username: {user.username}, Email: {user.email}")
