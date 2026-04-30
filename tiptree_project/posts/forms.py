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
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="補足説明"
    )
    
    class Meta:
        model = Post
        fields = ('title','parent_category','category','thumbnail','video','content')
        labels = {
            'title':'タイトル',
            'thumbnail':'サムネイル画像',
            'video':'動画',
            'content':'本文',
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }
        error_messages ={
            'title':{
                'required':'タイトルを入力してください。',
                'max_length':'タイトルは100字以内で書いてください。'
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
    
    def clean_video(self):
        video = self.cleaned_data.get('video')

        if not video:
            return video

        # 拡張子
        valid_extensions = ['.mp4', '.mov']
        if not any(video.name.lower().endswith(ext) for ext in valid_extensions):
            raise ValidationError('MP4またはMOV形式の動画をアップしてください。')

        # MIME
        if not video.content_type.startswith('video/'):
            raise ValidationError('動画ファイルを選択してください。')

        # 容量
        if video.size > 30 * 1024 * 1024:
            raise ValidationError('動画は30MB以内にしてください。')

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
        fields = ('title','parent_category','category','thumbnail','video','content')
        labels = {
            'title':'タイトル',
            'category':'サブカテゴリ',
            'thumbnail':'サムネイル画像',
            'video':'動画',
            'content':'本文',
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
            "thumbnail": forms.FileInput(),
            "video": forms.FileInput(),
        }
        error_messages ={
            'title':{
                'required':'タイトルを入力してください。',
                'max_length':'タイトルは100字以内で書いてください。'
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
            
        self.fields['parent_category'].widget.attrs.update({
            'id': 'parent-category'
        })

        self.fields['category'].widget.attrs.update({
            'id': 'child-category'
        })
            
        self.fields['thumbnail'].widget.attrs.update({
            'id': 'thumbnailInput'
        })

        self.fields['video'].widget.attrs.update({
            'id': 'videoInput'
        })
        
        if 'parent_category' in self.data:
            try:
                parent_id = int(self.data.get('parent_category'))
                self.fields['category'].queryset = Category.objects.filter(
                    parent_id=parent_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance and self.instance.pk:

            if self.instance.category.parent:
                # 子カテゴリ付き投稿
                self.fields['category'].queryset = Category.objects.filter(
                    parent=self.instance.category.parent
                )
                self.initial['parent_category'] = self.instance.category.parent

            else:
                # 親のみ投稿
                self.fields['category'].queryset = Category.objects.filter(parent=self.instance.category)
                self.initial['parent_category'] = self.instance.category
                self.initial['category'] = None


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