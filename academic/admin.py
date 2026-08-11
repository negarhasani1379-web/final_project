from django.contrib import admin

from .models import Term


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