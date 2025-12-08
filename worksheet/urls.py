from django.urls import path
from .views import GenerateLLMContentView, GenerateWorksheetView, RunSchedulerView

urlpatterns = [
    path(
        "generate-content/", GenerateLLMContentView.as_view(), name="generate-content"
    ),
    path(
        "generate-worksheet/",
        GenerateWorksheetView.as_view(),
        name="generate-worksheet",
    ),
    path("run-scheduler/", RunSchedulerView.as_view(), name="run-scheduler"),
]
