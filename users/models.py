from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)
    next_delivery = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.email
