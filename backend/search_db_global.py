import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.apps import apps

email_to_search = 'saipratap65@gmail.com'
print(f"--- Searching for email: {email_to_search} ---")

for model in apps.get_models():
    emails = [f.name for f in model._meta.get_fields() if f.name.endswith('email')]
    if emails:
        qs = model.objects.filter(**{f"{e}__icontains": email_to_search for e in emails})
        if qs.exists():
            print(f"\nModel: {model.__name__}")
            for obj in qs:
                fields = {f.name: getattr(obj, f.name) for f in model._meta.get_fields() if not f.is_relation}
                print(f"  ID: {obj.id}, Data: {fields}")

print("\n--- Additional search for token eea9546a in all UUID fields ---")
token_to_search = 'eea9546a-d97d-495c-86a9-0f650958c44a'
for model in apps.get_models():
    uuids = [f.name for f in model._meta.get_fields() if 'UUIDField' in str(type(f))]
    if uuids:
        qs = model.objects.filter(**{f"{u}": token_to_search for u in uuids})
        if qs.exists():
            print(f"\nModel: {model.__name__} (Found by Token)")
            for obj in qs:
                fields = {f.name: getattr(obj, f.name) for f in model._meta.get_fields() if not f.is_relation}
                print(f"  ID: {obj.id}, Data: {fields}")

