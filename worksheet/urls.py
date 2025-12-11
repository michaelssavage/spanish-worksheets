from django.urls import path
from .views import (
    GenerateLLMContentView,
    GenerateWorksheetEmailView,
    GenerateWorksheetView,
    RunSchedulerView,
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
    path("run-scheduler/", RunSchedulerView.as_view(), name="run-scheduler"),
]
