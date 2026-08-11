from django.contrib import admin

from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name",)
    list_filter = ("is_deleted",)
