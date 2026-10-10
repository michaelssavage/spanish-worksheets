from django.db import models

from users.models import User


class Worksheet(models.Model):
    class Language(models.TextChoices):
        SPANISH = "es", "Spanish"
        CATALAN = "ca", "Catalan"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(
        max_length=2, choices=Language.choices, default=Language.SPANISH
    )
    created_at = models.DateTimeField(auto_now_add=True)

    content_hash = models.CharField(max_length=64, unique=True)
    content = models.TextField(null=True, blank=True)

    topics = models.JSONField(null=True, blank=True)
    themes = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["user", "language", "-created_at"])]

    def __str__(self):
        return f"{self.user.email} ({self.language}) - {self.created_at.date()}"


class Config(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.key} = {self.value}"
