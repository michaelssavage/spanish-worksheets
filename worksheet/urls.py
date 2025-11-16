from django.urls import path
from .views import generate_llm_content, generate_worksheet, run_scheduler

urlpatterns = [
    path("generate-content/", generate_llm_content, name="generate-content"),
    path("generate-worksheet/", generate_worksheet, name="generate-worksheet"),
    path("run-scheduler/", run_scheduler, name="run-scheduler"),
]
