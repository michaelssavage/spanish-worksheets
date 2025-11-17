from django.db import models

from users.models import User


class Worksheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    content_hash = models.CharField(max_length=64, unique=True)

    topics = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.created_at.date()}"


class Config(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.key} = {self.value}"
