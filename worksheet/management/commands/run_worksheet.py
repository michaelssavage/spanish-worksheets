from django.core.management.base import BaseCommand
from users.models import User
from worksheet.services.generate import generate_worksheet_for
from worksheet.services.email import send_worksheet_email
from worksheet.models import Worksheet
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = timezone.now().date()
        users = User.objects.filter(active=True, next_delivery=today)

        for u in users:
            content = generate_worksheet_for(u)
            if content:
                # Get the worksheet to retrieve themes
                worksheet = (
                    Worksheet.objects.filter(user=u).order_by("-created_at").first()
                )
                themes = worksheet.themes if worksheet and worksheet.themes else None
                send_worksheet_email(u, content, theme=themes)
            u.next_delivery = today + timedelta(days=2)
            u.save()

        self.stdout.write(self.style.SUCCESS("Done"))
