from django.core.management.base import BaseCommand
from users.models import User
from worksheet.services.generate import generate_worksheet_for
from worksheet.services.email import send_worksheet_email
from worksheet.services.languages import LANGUAGES
from worksheet.services.topic_rotator import get_and_increment_topic_index, themes_for
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        today = timezone.now().date()
        users = User.objects.filter(active=True, next_delivery=today)

        for u in users:
            topic_index = get_and_increment_topic_index()
            for lang in LANGUAGES.values():
                themes = themes_for(lang, topic_index)
                content = generate_worksheet_for(u, themes=themes, language=lang.code)
                if content and lang.sends_email:
                    send_worksheet_email(u, content, theme=themes)
            u.next_delivery = today + timedelta(days=2)
            u.save()

        self.stdout.write(self.style.SUCCESS("Done"))
