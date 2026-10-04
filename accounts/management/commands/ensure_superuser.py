"""Create the site admin from environment variables if it doesn't exist.

Used during deployment on hosts without a shell (such as Render's free
plan), where `createsuperuser` can't be run interactively. Running it again
does nothing, so it is safe on every deploy.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command: `python manage.py ensure_superuser`."""

    help = (
        "Create a superuser from DJANGO_SUPERUSER_USERNAME, "
        "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD if it "
        "does not already exist."
    )

    def handle(self, *args, **options):
        """Create the superuser, or explain why nothing was done."""
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "Superuser variables not set; skipping admin creation."
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists.")
            return

        User.objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{username}' created.")
        )
