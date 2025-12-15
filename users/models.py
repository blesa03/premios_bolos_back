from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField("Apodo", max_length=30, blank=True)
    short_bio = models.CharField("Descripción corta", max_length=20, blank=True)
    long_bio = models.CharField("Descripción larga", max_length=120, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.username or self.nickname or f"User {self.pk}"
