from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from account.models import User, UserRole
from core.models import BaseModel, SoftDeleteModel
from school.models import School


class TermType(models.TextChoices):
    NORMAL = "normal", "Normal"
    SUMMER = "summer", "Summer"


class Term(SoftDeleteModel):
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    term_type = models.CharField(
        max_length=10,
        choices=TermType.choices,
    )
    
    def clean(self):
        super().clean()

        if self.end_date < self.start_date:
            raise ValidationError(
                "End date cannot be before start date."
            )

        if self.start_date.day != 1:
            raise ValidationError(
                "Term must start on the first day of a month."
            )

        next_month = self.start_date.month % 12 + 1
        next_month_year = self.start_date.year + (
            1 if self.start_date.month == 12 else 0
        )

        expected_end_date = date(
            next_month_year,
            next_month,
            1,
        ) - timedelta(days=1)

        if self.end_date != expected_end_date:
            raise ValidationError(
                "Term must end on the last day of the same month."
            )

        overlapping = Term.objects.filter(
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                "This term overlaps with an existing term."
            )

class Class(SoftDeleteModel):
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

    
    session_duration = models.PositiveIntegerField(
        choices=[
            (60, "60 minutes"),
            (90, "90 minutes"),
            (120, "120 minutes"),
        ]
    )


class Session(SoftDeleteModel):
    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="sessions",
    )

    session_number = models.PositiveIntegerField()

    session_date = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "session_number"],
                name="unique_session_number_per_class",
            ),
            models.UniqueConstraint(
                fields=["classroom", "session_date"],
                name="unique_session_date_per_class",
            ),
        ]    

class TeacherAssignment(SoftDeleteModel):
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
    def clean(self):
        super().clean()

        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                "End date cannot be before start date."
            )
        if self.classroom_id and self.start_date:
            overlapping = TeacherAssignment.objects.filter(
                classroom_id=self.classroom_id,
                start_date__lte=self.end_date or date.max,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=self.start_date)
            )

            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    "This classroom already has a teacher assigned "
                    "during this period."
                )