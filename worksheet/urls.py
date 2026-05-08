from django.urls import path
from .views import (
    GenerateLLMContentView,
    GenerateWorksheetEmailView,
    GenerateAndSendWorksheetView,
    LatestWorksheetView,
    WorksheetJobStatusView,
)

urlpatterns = [
    # No generation or email; returns the most recent worksheet (parsed JSON).
    path(
        "",
        LatestWorksheetView.as_view(),
        name="latest",
    ),
    # No generation; emails the user’s most recently saved worksheet.
    path(
        "email/",
        GenerateWorksheetEmailView.as_view(),
        name="email",
    ),
    # Persists worksheet; no email; returns generated content in the response.
    path(
        "regenerate/",
        GenerateLLMContentView.as_view(),
        name="regenerate",
    ),
    # Full flow: enqueue generation job; worker saves worksheet and sends email.
    path(
        "delivery/",
        GenerateAndSendWorksheetView.as_view(),
        name="delivery",
    ),
    path(
        "delivery/<str:job_id>/",
        WorksheetJobStatusView.as_view(),
        name="delivery-status",
    ),
]
