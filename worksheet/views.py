from worksheet.jobs import generate_worksheet_job
from worksheet.serializers import (
    GenerateCustomWorksheetRequestSerializer,
    GenerateCustomWorksheetResponseSerializer,
    GenerateLLMContentRequestSerializer,
    GenerateLLMContentResponseSerializer,
    GenerateWorksheetResponseSerializer,
    WorksheetLanguageQuerySerializer,
    WorksheetSerializer,
)
from django_rq import enqueue, get_queue
from rq.job import Job
from rq.exceptions import NoSuchJobError
from worksheet.services.generate import (
    generate_custom_exercises,
    generate_worksheet_for,
)
from worksheet.services.email import send_worksheet_email
from worksheet.models import Worksheet
from worksheet.services.languages import LANGUAGES
from worksheet.services.topic_rotator import get_and_increment_topic_index, themes_for
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class GenerateCustomWorksheetView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateCustomWorksheetRequestSerializer
    response_serializer = GenerateCustomWorksheetResponseSerializer

    def post(self, request):
        logger.info("generate_custom_worksheet called by user: %s", request.user.email)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_text = serializer.validated_data["request"]
        language = serializer.validated_data["language"]
        content = generate_custom_exercises(request_text, language)

        if content is None:
            logger.warning(
                "Custom worksheet generation failed for %s", request.user.email
            )
            return Response(
                {"error": "Custom worksheet generation failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            self.response_serializer(
                {"request": request_text, "language": language, "content": content}
            ).data
        )


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
        language = serializer.validated_data["language"]

        content = generate_worksheet_for(
            request.user, themes=themes_arg, language=language
        )

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

        # One job per language so a slow or failed language can't block the other.
        # The topic index is advanced once here so every language shares themes.
        topic_index = get_and_increment_topic_index()
        jobs = {
            code: enqueue(
                generate_worksheet_job,
                request.user.id,
                code,
                themes_for(lang, topic_index),
            ).id
            for code, lang in LANGUAGES.items()
        }

        return Response(
            {
                "message": "Worksheet generation started",
                "jobs": jobs,
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
            Worksheet.objects.filter(
                user=request.user, language=Worksheet.Language.SPANISH
            )
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


class LatestWorksheetView(RetrieveAPIView):
    """Return the authenticated user's most recent worksheet for ?language= (default es)."""

    permission_classes = [IsAuthenticated]
    serializer_class = WorksheetSerializer

    def get_queryset(self):
        return Worksheet.objects.filter(user=self.request.user).select_related("user")

    def get_object(self):
        query = WorksheetLanguageQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        language = query.validated_data["language"]

        worksheet = (
            self.get_queryset()
            .filter(language=language)
            .exclude(content__isnull=True)
            .exclude(content="")
            .order_by("-created_at")
            .first()
        )
        if worksheet is None:
            raise NotFound("No worksheet available")
        return worksheet
