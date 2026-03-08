from django.db import models
from django.db import models
from posts.models import User,Post,Comments,Supplements


class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ("comment", "コメント"),
        ("comment_reply", "コメントへの返信"),
        ("supplement", "補足説明"),
        ("supplement_reply", "補足説明への返信"),
        ("help", "役立った"),
        ("save", "保存"),
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    comment = models.ForeignKey(
        Comments,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    supplement = models.ForeignKey(
        Supplements,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_message(self):
        if self.notification_type == "comment":
            return f"{self.from_user.username}さんが「{self.post.title}」にコメントしました"

        if self.notification_type == "comment_reply":
            return f"{self.from_user.username}さんがあなたのコメントに返信しました"

        if self.notification_type == "supplement":
            return f"{self.from_user.username}さんが「{self.post.title}」に補足情報を追加しました"
        
        if self.notification_type == "supplement_reply":
            return f"{self.from_user.username}さんがあなたの補足情報に返信しました"

        if self.notification_type == "help":
            return f"{self.from_user.username}さんが「{self.post.title}」に役立ったを付けました"

        if self.notification_type == "save":
            return f"{self.from_user.username}さんが「{self.post.title}」を保存しました"

        return ""

    def __str__(self):
        return f"{self.to_user} ← {self.from_user} ({self.notification_type})"