"""
Management command to create a superuser in production.
This can be run non-interactively using environment variables.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser in production using environment variables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            help="Email address for the superuser",
            default=config("SUPERUSER_EMAIL", default=None),
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password for the superuser",
            default=config("SUPERUSER_PASSWORD", default=None),
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Run non-interactively (requires --email and --password or env vars)",
        )

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        no_input = options["no_input"]

        # Check if superuser already exists
        if User.objects.filter(email=email, is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING(f"Superuser with email {email} already exists.")
            )
            return

        # If no email/password provided and not in no-input mode, prompt
        if not email:
            if no_input:
                raise CommandError(
                    "Email is required. Provide --email or set SUPERUSER_EMAIL environment variable."
                )
            email = input("Email: ")

        if not password:
            if no_input:
                raise CommandError(
                    "Password is required. Provide --password or set SUPERUSER_PASSWORD environment variable."
                )
            from getpass import getpass

            password = getpass("Password: ")
            password_confirm = getpass("Password (again): ")
            if password != password_confirm:
                raise CommandError("Passwords do not match.")

        try:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(
                self.style.SUCCESS(f"Superuser {email} created successfully.")
            )
        except Exception as e:
            raise CommandError(f"Error creating superuser: {e}")
