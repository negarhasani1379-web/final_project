from django.contrib import admin

from .models import Salary, SessionReport, TeacherTermRate


@admin.register(TeacherTermRate)
class TeacherTermRateAdmin(admin.ModelAdmin):

    list_display = (
        "teacher",
        "term",
        "base_rate",
    )

    list_filter = (
        "term",
        "teacher",
    )

    search_fields = (
        "teacher__username",
        "term__title",
    )


@admin.register(SessionReport)
class SessionReportAdmin(admin.ModelAdmin):

    list_display = (
        "session",
        "teacher_assignment",
        "status",
        "is_late",
    )

    list_filter = (
        "status",
        "is_late",
    )

    search_fields = (
        "teacher_assignment__teacher__username",
        "lesson_summary",
    )


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):

    list_display = (
        "teacher",
        "term",
        "year",
        "month",
        "calculated_amount",
        "final_amount",
    )

    list_filter = (
        "year",
        "month",
        "term",
    )

    search_fields = (
        "teacher__username",
        "term__title",
    )