from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from users.models import User
from worksheet.services.generate import generate_worksheet_for, call_llm
from worksheet.services.email import send_worksheet_email
from worksheet.services.prompts import build_payload
from worksheet.services.topic_rotator import get_and_increment_topics


def run_scheduler(request):
    if request.GET.get("key") != settings.CRON_SECRET:
        return HttpResponseForbidden()

    today = timezone.now().date()
    users = User.objects.filter(active=True, next_delivery=today)

    for u in users:
        content = generate_worksheet_for(u)
        if content:
            send_worksheet_email(u, content)
        u.next_delivery = today + timedelta(days=2)
        u.save()

    return JsonResponse({"status": "ok"})


@csrf_exempt
def generate_llm_content(request):
    """Endpoint that calls the LLM and returns the content directly.

    Accepts POST with JSON body containing optional 'themes' array.
    If themes is empty or not provided, fetches a random theme pool.
    """
    # Parse themes from request body
    themes = []
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            themes = body.get("themes", [])
        except (json.JSONDecodeError, AttributeError):
            themes = []

    # If no themes provided, get a random theme pool
    if not themes:
        themes = get_and_increment_topics()

    payload = build_payload([], themes)
    content = call_llm(payload)
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
