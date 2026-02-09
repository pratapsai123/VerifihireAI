from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from api.models import ApplicationAdmin


class Command(BaseCommand):
    help = "Create the single Application SuperAdmin (ApplicationAdmin) record."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email/username for the Application Admin (can be gmail).")
        parser.add_argument("--password", required=True, help="Password for the Application Admin user.")
        parser.add_argument("--first-name", default="", help="Optional first name.")
        parser.add_argument("--last-name", default="", help="Optional last name.")

    def handle(self, *args, **options):
        email = (options["email"] or "").strip().lower()
        password = options["password"]
        first_name = options["first_name"] or ""
        last_name = options["last_name"] or ""

        if not email or "@" not in email:
            raise CommandError("Valid --email is required.")
        if not password:
            raise CommandError("--password is required.")

        if ApplicationAdmin.objects.exists():
            existing = ApplicationAdmin.objects.select_related("user").first()
            self.stdout.write(self.style.WARNING(f"ApplicationAdmin already exists: {existing}"))
            return

        user, created = User.objects.get_or_create(username=email, defaults={"email": email})
        if not created:
            user.email = user.email or email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        app_admin = ApplicationAdmin.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(f"Created ApplicationAdmin: {app_admin}"))


