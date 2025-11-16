from django.contrib import admin
from django.urls import path

from worksheet.views import run_scheduler, generate_llm_content

urlpatterns = [
    path("admin/", admin.site.urls),
    path("internal/run-scheduler/", run_scheduler),
    path("api/generate/", generate_llm_content),
]
