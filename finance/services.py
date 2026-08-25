from decimal import Decimal

from django.db import transaction

from account.models import User, UserRole
from finance.models import (
    Salary,
    SessionReport,
    SessionReportStatus,
    TeacherTermRate,
)


def calculate_teacher_monthly_salary_amount(
    teacher,
    year,
    month,
):
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")

    reports = (
        SessionReport.objects
        .filter(
            teacher_assignment__teacher=teacher,
            session__session_date__year=year,
            session__session_date__month=month,
        )
        .select_related(
            "session__classroom__term",
        )
    )

    if not reports.exists():
        raise ValueError(
            "No session reports found for this teacher in this month."
        )

    unapproved_reports = reports.exclude(
        status=SessionReportStatus.APPROVED,
    )

    if unapproved_reports.exists():
        raise ValueError(
            "Salary cannot be calculated until all reports "
            "for the month are approved."
        )

    term_ids = set(
        reports.values_list(
            "session__classroom__term_id",
            flat=True,
        )
    )

    if len(term_ids) != 1:
        raise ValueError(
            "Salary calculation requires reports from exactly one term."
        )

    term = reports.first().session.classroom.term

    teacher_term_rate = (
        TeacherTermRate.objects
        .filter(
            teacher=teacher,
            term=term,
            is_deleted=False,
        )
        .first()
    )

    if teacher_term_rate is None:
        raise ValueError(
            "No teacher term rate exists for this teacher and term."
        )

    base_rate = teacher_term_rate.base_rate

    count_60 = 0
    count_90 = 0
    count_120 = 0

    eligible_reports = reports.filter(
        status=SessionReportStatus.APPROVED,
        is_late=False,
    )

    for report in eligible_reports:
        duration = report.session.classroom.session_duration

        if duration == 60:
            count_60 += 1
        elif duration == 90:
            count_90 += 1
        elif duration == 120:
            count_120 += 1

    wage = (
        Decimal(count_90) * base_rate
        + Decimal(count_60) * (base_rate * Decimal("0.7"))
        + Decimal(count_120) * (base_rate * Decimal("1.3"))
    )

    if term.term_type == "summer":
        wage = wage * Decimal("1.1")

    return wage


def calculate_teacher_monthly_salary(
    teacher,
    year,
    month,
):
    wage = calculate_teacher_monthly_salary_amount(
        teacher=teacher,
        year=year,
        month=month,
    )

    term = (
        SessionReport.objects
        .filter(
            teacher_assignment__teacher=teacher,
            session__session_date__year=year,
            session__session_date__month=month,
            status=SessionReportStatus.APPROVED,
        )
        .select_related("session__classroom__term")
        .first()
        .session
        .classroom
        .term
    )

    salary, _ = Salary.objects.update_or_create(
        teacher=teacher,
        year=year,
        month=month,
        defaults={
            "term": term,
            "calculated_amount": wage,
            "final_amount": wage,
            "adjustment_reason": "",
        },
    )

    return salary


@transaction.atomic
def calculate_all_teachers_monthly_salary(year, month):
    teacher_ids = (
        SessionReport.objects
        .filter(
            session__session_date__year=year,
            session__session_date__month=month,
            teacher_assignment__teacher__role=UserRole.TEACHER,
        )
        .values_list(
            "teacher_assignment__teacher_id",
            flat=True,
        )
        .distinct()
    )

    if not teacher_ids:
        raise ValueError(
            "No teacher session reports found for this month."
        )

    teachers = User.objects.filter(
        id__in=teacher_ids,
        role=UserRole.TEACHER,
    )

    salaries = []

    for teacher in teachers:
        salary = calculate_teacher_monthly_salary(
            teacher=teacher,
            year=year,
            month=month,
        )
        salaries.append(salary)

    return salaries

def list_teacher_monthly_salaries(year, month):
    return Salary.objects.filter(
        year=year,
        month=month,
    ).select_related(
        "teacher",
        "term",
    )



