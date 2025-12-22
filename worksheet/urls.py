from django.urls import path
from .views import (
    GenerateLLMContentView,
    GenerateWorksheetEmailView,
    GenerateWorksheetView,
    WorksheetJobStatusView,
)

urlpatterns = [
    path(
        "generate-content/", GenerateLLMContentView.as_view(), name="generate-content"
    ),
    path(
        "generate-worksheet/",
        GenerateWorksheetView.as_view(),
        name="generate-worksheet",
    ),
    path(
        "send-worksheet-email/",
        GenerateWorksheetEmailView.as_view(),
        name="generate-worksheet-email",
    ),
    path(
        "worksheet-job-status/<str:job_id>/",
        WorksheetJobStatusView.as_view(),
        name="worksheet-job-status",
    ),
]
