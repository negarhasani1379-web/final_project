from django.db import models

from academic.models import TeacherAssignment, Term
from account.models import User, UserRole
from core.models import BaseModel, SoftDeleteModel


class TeacherTermRate(SoftDeleteModel):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="term_rates",
        limit_choices_to={"role": UserRole.TEACHER},
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name="teacher_rates",
    )

    base_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "term"],
                name="unique_teacher_term_rate",
            )
        ]


class SessionReport(BaseModel):
    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.CASCADE,
        related_name="session_reports",
    )

    session_date = models.DateField()

    session_number = models.PositiveIntegerField()

    lesson_summary = models.TextField()

    present_count = models.PositiveIntegerField()

    absent_count = models.PositiveIntegerField()

    status = models.CharField(max_length=30)

    review_comment = models.TextField(
        blank=True,
    )

    is_late = models.BooleanField(default=False)        



class Salary(BaseModel):
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="salaries",
        limit_choices_to={"role": UserRole.TEACHER},
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        related_name="salaries",
    )

    month = models.PositiveSmallIntegerField()

    calculated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    adjustment_reason = models.TextField(
        blank=True,
    )