from worksheet.models import Worksheet
from worksheet.services.prompts import build_payload
from django.conf import settings
import hashlib
from openai import OpenAI

from worksheet.services.topic_rotator import get_and_increment_topics


def call_llm(predictions_payload):
    # DeepSeek is OpenAI-compatible:
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=predictions_payload,
        temperature=0.7,
    )

    return response.choices[0].message.content


def generate_worksheet_for(user):
    recent = Worksheet.objects.filter(user=user).order_by("-created_at")[:10]
    forbidden = []

    for w in recent:
        if w.content_preview:
            forbidden.append(w.content_preview)

    themes = get_and_increment_topics()
    payload = build_payload(forbidden, themes)
    content = call_llm(payload)

    # Important: content is machine-readable JSON output from the model
    h = hashlib.sha256(content.encode("utf-8")).hexdigest()

    if Worksheet.objects.filter(content_hash=h).exists():
        return None

    Worksheet.objects.create(
        user=user,
        content_hash=h,
        content_preview=content[:200],
        topics=["past", "present_future", "vocab"],
    )

    return content
