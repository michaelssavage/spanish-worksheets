from django.contrib import admin
from recipients.models import UserRecipient


@admin.register(UserRecipient)
class UserRecipientAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["email", "name", "user__email"]
    raw_id_fields = ["user"]
