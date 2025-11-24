"""
Management command to create a superuser in production.
Always uses SUPERUSER_EMAIL and SUPERUSER_PASSWORD environment variables.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser in production using environment variables"

    def handle(self, *args, **options):
        email = config("SUPERUSER_EMAIL", default=None)
        password = config("SUPERUSER_PASSWORD", default=None)

        if not email:
            raise CommandError("SUPERUSER_EMAIL environment variable is required.")

        if not password:
            raise CommandError("SUPERUSER_PASSWORD environment variable is required.")

        # Check if superuser already exists
        if User.objects.filter(email=email, is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(f"Superuser with email {email} already exists.")
            )
            return

        try:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(
                self.style.SUCCESS(f"Superuser {email} created successfully.")
            )
        except Exception as e:
            raise CommandError(f"Error creating superuser: {e}")
