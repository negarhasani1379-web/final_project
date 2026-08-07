from django.db import models

from account.models import User, UserRole
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

class TeacherAssignment(BaseModel):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assignments",
        limit_choices_to={"role": UserRole.TEACHER},
    )

    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )