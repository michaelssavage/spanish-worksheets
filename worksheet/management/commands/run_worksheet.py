from django.core.management.base import BaseCommand
from users.models import User
from worksheet.services.generate import generate_worksheet_for
from worksheet.services.email import send_worksheet_email
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = timezone.now().date()
        users = User.objects.filter(active=True, next_delivery=today)

        for u in users:
            content = generate_worksheet_for(u)
            if content:
                send_worksheet_email(u, content)
            u.next_delivery = today + timedelta(days=2)
            u.save()

        self.stdout.write(self.style.SUCCESS("Done"))
