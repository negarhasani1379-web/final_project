from django.db import models

from academic.models import Term
from account.models import User, UserRole
from core.models import BaseModel


class TeacherTermRate(BaseModel):
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



