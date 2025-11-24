from django.utils import timezone
from datetime import timedelta
from users.models import User
from worksheet.services.generate import generate_worksheet_for, call_llm
from worksheet.services.email import send_worksheet_email
from worksheet.services.prompts import build_payload
from worksheet.services.topic_rotator import get_and_increment_topics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def run_scheduler(request):
    today = timezone.now().date()
    logger.info(f"Starting scheduler for date: {today}")
    users = User.objects.filter(active=True, next_delivery=today)
    user_count = users.count()

    for u in users:
        logger.info(f"Processing user: {u.email} (ID: {u.id})")
        content = generate_worksheet_for(u)
        if content:
            logger.info(
                f"Worksheet generated successfully for {u.email}, sending email"
            )
            send_worksheet_email(u, content)
        else:
            logger.warning(
                f"Duplicate worksheet detected for {u.email}, skipping email"
            )
        u.next_delivery = today + timedelta(days=2)
        u.save()
        logger.info(f"Updated next_delivery for {u.email} to {u.next_delivery}")

    logger.info(f"Scheduler completed. Processed {user_count} users")
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_llm_content(request):
    """Endpoint that calls the LLM and returns the content directly.

    Accepts POST with JSON body containing optional 'themes' array.
    If themes is empty or not provided, fetches a random theme pool.
    """
    logger.info(f"generate_llm_content called by user: {request.user.email}")
    # Parse themes from request body
    themes = []
    try:
        themes = request.data.get("themes", [])
    except (AttributeError, KeyError):
        themes = []

    # If no themes provided, get a random theme pool
    if not themes:
        logger.info("No themes provided, fetching from topic rotator")
        themes = get_and_increment_topics()
    else:
        logger.info(f"Using provided themes: {themes}")

    logger.info(f"Building payload with themes: {themes}")
    payload = build_payload([], themes)
    content = call_llm(payload)
    logger.info(f"LLM content generated successfully (length: {len(content)} chars)")
    return Response({"content": content}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_worksheet(request):
    logger.info(f"generate_worksheet called by user: {request.user.email}")
    content = generate_worksheet_for(request.user)

    if content is None:
        logger.warning(f"Duplicate worksheet detected for user: {request.user.email}")
        return Response(
            {"error": "Duplicate worksheet detected"}, status=status.HTTP_409_CONFLICT
        )

    logger.info(
        f"Worksheet generated successfully for {request.user.email} (length: {len(content)} chars)"
    )

    try:
        send_worksheet_email(request.user, content)
        logger.info(f"Email sent successfully to {request.user.email}")
    except Exception as e:
        logger.error(f"Failed to send email to {request.user.email}: {e}")

    return Response({"content": content}, status=status.HTTP_200_OK)
