from django.db import models

from core.models import BaseModel
from school.models import School


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
    
    def __str__(self):
        return self.title
    

class Class(BaseModel):
    title = models.CharField(max_length=100)

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classes",
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name="classes",
    )

    session_duration = models.PositiveIntegerField()    