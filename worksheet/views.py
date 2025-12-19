from django.utils import timezone
from datetime import timedelta

from drf_spectacular.utils import extend_schema
from users.models import User
from worksheet.serializers import (
    GenerateLLMContentRequestSerializer,
    GenerateLLMContentResponseSerializer,
    GenerateWorksheetResponseSerializer,
    SchedulerResponseSerializer,
)
from worksheet.services.generate import generate_worksheet_for, call_llm
from worksheet.services.email import send_worksheet_email
from worksheet.services.prompts import build_payload
from worksheet.services.topic_rotator import get_and_increment_topics
from worksheet.models import Worksheet
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class RunSchedulerView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SchedulerResponseSerializer

    def get(self, request):
        today = timezone.now().date()
        logger.info(f"Starting scheduler: {today}")

        users = User.objects.filter(active=True, next_delivery=today)

        for u in users:
            content = generate_worksheet_for(u)
            if content:
                send_worksheet_email(u, content)
            u.next_delivery = today + timedelta(days=2)
            u.save()

        return Response({"status": "ok"})


class GenerateLLMContentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateLLMContentRequestSerializer
    response_serializer = GenerateLLMContentResponseSerializer

    def post(self, request):
        logger.info(f"generate_llm_content called by user: {request.user.email}")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        themes = serializer.validated_data.get("themes", [])
        if not themes:
            logger.info("No themes provided, fetching from topic rotator")
            themes = get_and_increment_topics()

        payload = build_payload(themes)
        content = call_llm(payload)

        logger.info(
            f"LLM content generated successfully (length: {len(content)} chars)"
        )

        return Response({"content": content})


@extend_schema(
    request=None,
    responses=GenerateWorksheetResponseSerializer,
)
class GenerateWorksheetView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateWorksheetResponseSerializer

    def post(self, request):
        logger.info(f"generate_worksheet called by user: {request.user.email}")

        content = generate_worksheet_for(request.user)

        if content is None:
            return Response(
                {"error": "Duplicate worksheet detected"},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            send_worksheet_email(request.user, content)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

        return Response({"content": content})


class GenerateWorksheetEmailView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateWorksheetResponseSerializer

    def post(self, request):
        logger.info(f"send_worksheet_email called by user: {request.user.email}")

        worksheet = (
            Worksheet.objects.filter(user=request.user)
            .order_by("-created_at")
            .only("content")
            .first()
        )

        if not worksheet or not worksheet.content:
            logger.warning(
                f"No worksheet found for user {request.user.email}; cannot send email"
            )
            return Response(
                {"error": "No worksheet available"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            send_worksheet_email(request.user, worksheet.content)
        except Exception as e:
            logger.error(f"Failed to resend worksheet email: {e}")
            return Response(
                {"error": "Failed to send email"}, status=status.HTTP_502_BAD_GATEWAY
            )

        return Response({"content": worksheet.content})
