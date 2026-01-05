from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import User
from worksheet.services.generate import generate_worksheet_for
from worksheet.services.email import send_worksheet_email
from worksheet.models import Worksheet


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "active", "is_staff", "is_superuser")
    list_filter = ("active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
        ("Other", {"fields": ("next_delivery",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")
    actions = ["generate_and_send_worksheet"]

    @admin.action(description="Generate worksheet and send email for selected users")
    def generate_and_send_worksheet(self, request, queryset):
        """Admin action to generate worksheet and send email for selected users."""
        success_count = 0
        error_count = 0

        for user in queryset:
            try:
                content = generate_worksheet_for(user)
                if content:
                    # Get the worksheet to retrieve themes
                    worksheet = (
                        Worksheet.objects.filter(user=user)
                        .order_by("-created_at")
                        .first()
                    )
                    themes = (
                        worksheet.themes if worksheet and worksheet.themes else None
                    )
                    send_worksheet_email(user, content, theme=themes)
                    # Update next_delivery date
                    today = timezone.now().date()
                    user.next_delivery = today + timedelta(days=2)
                    user.save()
                    success_count += 1
                else:
                    self.message_user(
                        request,
                        f"Duplicate worksheet detected for {user.email}, skipping.",
                        messages.WARNING,
                    )
                    error_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error processing {user.email}: {str(e)}",
                    messages.ERROR,
                )
                error_count += 1

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully generated and sent worksheets to {success_count} user(s).",
                messages.SUCCESS,
            )
        if error_count > 0:
            self.message_user(
                request,
                f"Failed to process {error_count} user(s).",
                messages.ERROR,
            )
