from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "to_user",
        "from_user",
        "notification_type",
        "is_read",
        "created_at",
    )
