from django.contrib import admin
from .models import Worksheet, Config


@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "content_hash_short", "topics")
    list_filter = ("created_at", "user")
    search_fields = ("user__email", "content_hash")
    readonly_fields = ("created_at", "content_hash", "topics", "user")
    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Information", {"fields": ("user", "created_at")}),
        ("Content", {"fields": ("content_hash", "topics")}),
    )

    def content_hash_short(self, obj):
        """Display shortened content hash for list view"""
        return f"{obj.content_hash[:16]}..." if obj.content_hash else "-"

    content_hash_short.short_description = "Content Hash"


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key", "value")
