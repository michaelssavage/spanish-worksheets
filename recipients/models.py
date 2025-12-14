from django.db import models

from users.models import User


class UserRecipient(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_recipients"
    )
    email = models.EmailField()
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "email"]
