from django.db import models

from core.models import BaseModel


class TermType(models.TextChoices):
    NORMAL = "normal", "Normal"
    SUMMER = "summer", "Summer"


class Term(BaseModel):
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    term_type = models.CharField(
        max_length=10,
        choices=TermType.choices,
    )
    base_rate = models.PositiveIntegerField()

    def __str__(self):
        return self.title