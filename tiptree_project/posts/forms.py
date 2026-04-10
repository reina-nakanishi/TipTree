from django import forms
from .models import Post,Supplements,Comments,SupplementReply,CommentReply,Category
from tempfile import NamedTemporaryFile
import subprocess, json, os
from django.core.exceptions import ValidationError


class CreatePostForm(forms.ModelForm):
    
    parent_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent__isnull=True),
        required=True,
        widget=forms.Select(attrs={"id": "parent-category"}),
        label="カテゴリ"
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "child-category"}),
        label="サブカテゴリ"
    )
    
    class Meta:
        model = Post
        fields = ('title','parent_category','category','thumbnail','video','content','description')
        labels = {
            'title':'タイトル',
            'thumbnail':'サムネイル画像',
            'video':'動画',
            'content':'本文',
            'description':'補足説明'
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        error_messages ={
            'title':{
                'required':'タイトルを入力してください。',
                'max_length':'タイトルは100字以内で書いてください。'
            },
            'category':{
                'required':'カテゴリーを選択してください。'
            },
            'thumbnail':{
                'required':'サムネイル画像を選択してください。'
            },
            'video':{
                'required':'動画ファイルを選択してください。'
            },
            'content':{
                'required':'本文を入力してください。'
            }
        }
    
    def __init__(self, *args, validate_file=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_file = validate_file
        
        self.fields['thumbnail'].widget.attrs.update({
            'id': 'thumbnailInput'
        })

        self.fields['video'].widget.attrs.update({
            'id': 'videoInput'
        })
        
        if not validate_file:
            self.fields['thumbnail'].required = False
            self.fields['video'].required = False
            
        if 'parent_category' in self.data:
            try:
                parent_id = int(self.data.get('parent_category'))
                self.fields['category'].queryset = Category.objects.filter(parent_id=parent_id)
            except (ValueError, TypeError):
                pass
                    
    def get_video_duration(self,file):
        from tempfile import NamedTemporaryFile
        import subprocess, json, os
        
        with NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
                tmp_path = tmp.name
                
        try:
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
            
            print(result.stdout)
            print("STDERR",result.stderr)
            
            info = json.loads(result.stdout)
            duration = float(info.get("format",{}).get("duration",0))
            
        except Exception as e:
            print("ffprobe error:",e)
            duration = None
    
        finally:
            os.remove(tmp_path)
            
        return duration
    
    def clean_video(self):
        video = self.cleaned_data.get('video')
        
        if not self.validate_file:
            return video
        
        if not video:
            return video
        
        valid_extentions = ['mp4','mov','avi']
        if not any(video.name.lower().endswith(ext) for ext in valid_extentions):
            raise ValidationError('対応している動画形式はMP4,MOV,AVIです。')

        duration = self.get_video_duration(video)
        if duration is None:
            raise ValidationError('有効な動画ファイルを選択してください。')
        if duration > 60:
            raise ValidationError('動画は1分以内にしてください。')
        
        return video
    
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        
        if not thumbnail:
            return thumbnail
        
        valid_extentions = ['jpg','jpeg','png']
        if not self.validate_file:
            return thumbnail
        
        if not any(thumbnail.name.lower().endswith(ext) for ext in valid_extentions):
            raise ValidationError('対応している画像形式はJPEGとPNGです。')
        
        return thumbnail
                    
        
class EditPostForm(forms.ModelForm):
    
    parent_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent=None),
        label="カテゴリ"
    )
    
    class Meta:
        model = Post
        fields = ('title','parent_category','category','thumbnail','video','content','description')
        labels = {
            'title':'タイトル',
            'category':'サブカテゴリ',
            'thumbnail':'サムネイル画像',
            'video':'動画',
            'content':'本文',
            'description':'補足説明'
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "thumbnail": forms.FileInput(),
            "video": forms.FileInput(),
        }
        error_messages ={
            'title':{
                'required':'タイトルを入力してください。',
                'max_length':'タイトルは100字以内で書いてください。'
            },
            'category':{
                'required':'カテゴリーを選択してください。'
            },
            'thumbnail':{
                'required':'サムネイル画像を選択してください。'
            },
            'video':{
                'required':'動画ファイルを選択してください。'
            },
            'content':{
                'required':'本文を入力してください。'
            }
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.category:
            self.fields["parent_category"].initial = self.instance.category.parent


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 1,
                    'class':'auto-resize',
                    'placeholder': 'コメントを入力'
                }
            )
        }
        
class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 1,
                    'class':'auto-resize',
                }
            )
        }


class SupplementForm(forms.ModelForm):
    class Meta:
        model = Supplements
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 1,
                    'class':'auto-resize',
                    'placeholder': 'もっとこうしたら良くなる！'
                }
            )
        }
        
class SupplementReplyForm(forms.ModelForm):
    class Meta:
        model = SupplementReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 1,
                    'class':'auto-resize',
                }
            )
        }