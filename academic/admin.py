from django.contrib import admin

from .models import Class, Session, TeacherAssignment, Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "start_date",
        "end_date",
        "term_type",
    )
    list_filter = ("term_type",)
    search_fields = ("title",)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "school",
        "term",
        "session_duration",
    )

    list_filter = (
        "term",
        "session_duration",
    )

    search_fields = (
        "title",
    )

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "classroom",
        "start_date",
        "end_date",
    )

    list_filter = (
        "start_date",
        "end_date",
    )

    search_fields = (
        "teacher__username",
        "classroom__title",
    )

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):

    list_display = (
        "classroom",
        "session_number",
        "session_date",
    )

    list_filter = (
        "classroom",
        "session_date",
    )

    search_fields = (
        "classroom__title",
    )        