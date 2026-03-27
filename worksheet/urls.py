from django.urls import path
from .views import (
    GenerateLLMContentView,
    GenerateWorksheetEmailView,
    GenerateAndSendWorksheetView,
    LatestWorksheetView,
    WorksheetJobStatusView,
)

urlpatterns = [
    path(
        "generate-content/", GenerateLLMContentView.as_view(), name="generate-content"
    ),
    path(
        "generate-worksheet/",
        GenerateAndSendWorksheetView.as_view(),
        name="generate-worksheet",
    ),
    path(
        "send-worksheet-email/",
        GenerateWorksheetEmailView.as_view(),
        name="generate-worksheet-email",
    ),
    path("latest/", LatestWorksheetView.as_view(), name="latest-worksheet"),
    path(
        "worksheet-job-status/<str:job_id>/",
        WorksheetJobStatusView.as_view(),
        name="worksheet-job-status",
    ),
]
