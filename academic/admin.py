from django.contrib import admin

from .models import Class, Term


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