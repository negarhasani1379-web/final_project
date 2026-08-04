from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import BaseModel


class UserRole(models.TextChoices):
    TEACHER = "teacher", "Teacher"
    EDUCATION = "education", "Education Officer"
    FINANCE = "finance", "Finance Officer"


class User(AbstractUser, BaseModel):
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
    )
    phone = models.CharField(
        max_length=11,
        unique=True,
    )
    emergency_phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username
