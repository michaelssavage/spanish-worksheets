from worksheet.jobs import generate_worksheet_job
from worksheet.serializers import (
    GenerateLLMContentRequestSerializer,
    GenerateLLMContentResponseSerializer,
    GenerateWorksheetResponseSerializer,
)
from django_rq import enqueue, get_queue
from rq.job import Job
from worksheet.services.generate import call_llm
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


# Return the content to the user, no email is sent
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


class GenerateWorksheetView(GenericAPIView):
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
        job = Job.fetch(job_id, connection=queue.connection)

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
