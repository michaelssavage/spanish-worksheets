from django.contrib import admin
from django.urls import include, path

from rest_framework.authtoken.views import obtain_auth_token

from .views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/token/", obtain_auth_token, name="api-token"),
    path("api/worksheet/", include("worksheet.urls")),
]
