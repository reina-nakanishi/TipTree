from django.db import models
from accounts.models import User
from django.core.validators import FileExtensionValidator
import tempfile
import subprocess
import json
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self',
        on_delete = models.PROTECT,
        null = True,
        blank = True,
        related_name = 'subcategories'
    )
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name}:{self.name}"
        return self.name


def validate_video_duration(value):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            for chunk in value.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
            
        result = subprocess.run(
            [
                'ffprobe',
                '-v','error',
                '-show_entries','format=duration',
                '-of','json',
                tmp_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        info = json.loads(result.stdout or '{}')
        duration = float(info.get('format',{}).get('duration', 0))
        
        if duration == 0:
            raise ValidationError('動画を確認できませんでした。')
        
        if duration > 60:
            raise ValidationError('動画は1分以内にしてください。')
        
    except ValidationError:
        raise
    
    except Exception:
        raise ValidationError('動画を確認できませんでした。')
    

class Post(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    thumbnail = models.FileField(
        upload_to='posts/thumbnails/',
        validators=[FileExtensionValidator(['jpg','jpeg','png'],message="JPEGまたはPNG画像を選択してください")])
    video = models.FileField(
        upload_to='posts/videos/',
        validators=[FileExtensionValidator(['mp4','mov','avi'],message="MP4,MOV,AVIから動画を選択してください"),validate_video_duration])
    content = models.TextField()
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    uppdated_at = models.DateTimeField(auto_now=True)
    saved_users = models.ManyToManyField(
        User,
        through="SavePost",
        related_name="saved_posts"
    )
    helped_users = models.ManyToManyField(
        User,
        through="HelpPost",
        related_name="helped_posts"
    )
    
    @property
    def help_count(self):
        return self.helped_by.count()
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    class Meta:
        db_table = 'post'
        
        
class HelpPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='help_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='helped_by')
    created_at = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        db_table = 'help_posts'
        unique_together = ('user','post')
        
        
class SavePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='save_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'save_posts'
        unique_together = ('user','post')
        
        
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comments'