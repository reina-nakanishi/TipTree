from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        to_user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications
        }
    )

@login_required
def notification_redirect(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        to_user=request.user
    )

    # 既読にする
    if not notification.is_read:
        notification.is_read = True
        notification.save()

    # 遷移先（今は投稿詳細）
    return redirect("posts:post_detail", post_id=notification.post.id)