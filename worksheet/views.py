from worksheet.jobs import generate_worksheet_job
from worksheet.serializers import (
    GenerateLLMContentRequestSerializer,
    GenerateLLMContentResponseSerializer,
    GenerateWorksheetResponseSerializer,
)
from django_rq import enqueue, get_queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from worksheet.services.generate import generate_worksheet_for
from worksheet.services.email import send_worksheet_email
from worksheet.models import Worksheet
from worksheet.services.exercise_items import parse_worksheet_content
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


# Persists worksheet for the user; does not send email (see GenerateAndSendWorksheetView / job).
class GenerateLLMContentView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateLLMContentRequestSerializer
    response_serializer = GenerateLLMContentResponseSerializer

    def post(self, request):
        logger.info(f"generate_llm_content called by user: {request.user.email}")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        themes = serializer.validated_data.get("themes", [])
        themes_arg = themes if themes else None

        content = generate_worksheet_for(request.user, themes=themes_arg)

        if content is None:
            logger.warning(
                "Worksheet generation failed or duplicate for %s", request.user.email
            )
            return Response(
                {"error": "Worksheet generation failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        logger.info(
            "Worksheet saved (length: %s chars), no email sent",
            len(content),
        )

        return Response({"content": content})


class GenerateAndSendWorksheetView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"generate_worksheet called by user: {request.user.email}")

        job = enqueue(generate_worksheet_job, request.user.id)

        return Response(
            {
                "message": "Worksheet generation started",
                "job_id": job.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class WorksheetJobStatusView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        queue = get_queue("default")
        try:
            job = Job.fetch(job_id, connection=queue.connection)
        except NoSuchJobError:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": job.get_status(),
                "result": job.result,
                "failed": job.is_failed,
            }
        )


# No llm request send, only send an existing worksheet email to the user
class GenerateWorksheetEmailView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateWorksheetResponseSerializer

    def post(self, request):
        logger.info(f"send_worksheet_email called by user: {request.user.email}")

        worksheet = (
            Worksheet.objects.filter(user=request.user)
            .order_by("-created_at")
            .only("content", "themes")
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
            themes = worksheet.themes if worksheet.themes else None
            send_worksheet_email(request.user, worksheet.content, theme=themes)
        except Exception as e:
            logger.error(f"Failed to resend worksheet email: {e}")
            return Response(
                {"error": "Failed to send email"}, status=status.HTTP_502_BAD_GATEWAY
            )

        return Response({"content": worksheet.content})


class LatestWorksheetView(GenericAPIView):
    """Return the authenticated user's most recently saved worksheet (including answers)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        worksheet = (
            Worksheet.objects.filter(user=request.user).order_by("-created_at").first()
        )
        if not worksheet or not worksheet.content:
            return Response(
                {"error": "No worksheet available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        parsed = parse_worksheet_content(worksheet.content)
        if parsed is None:
            logger.error(
                "Stored worksheet %s for %s is not valid JSON",
                worksheet.id,
                request.user.email,
            )
            return Response(
                {"error": "Worksheet content is invalid"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "id": worksheet.id,
                "created_at": worksheet.created_at,
                "themes": worksheet.themes,
                "topics": worksheet.topics,
                "content": parsed,
            }
        )
