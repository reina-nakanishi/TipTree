from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
import re


User = get_user_model()

class RegistForm(forms.ModelForm):
    password1 = forms.CharField(label='パスワード', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,error_messages={
                                   'invalid':'パスワードは半角英数字8字以上50字以下で入力してください',
                               },
                               validators=[
                                   RegexValidator(
                                       regex=r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
                                       message='パスワードは半角英数字両方含めてください'
                                   )])
    password2 = forms.CharField(label='パスワード再入力', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,)
    
    class Meta:
        model = User
        fields = ('username','email')
        labels = {'username':'アカウント名', 'email':'メールアドレス'}
            
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError('パスワードが一致しません')
        
    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password1'))
        user.save()
        return user



class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス",
                             error_messages={
                                 'reqired' : 'メールアドレスを入力してください',
                                 'invalid' : '有効なメールアドレスを入力してください'
                             })
    password = forms.CharField(label="パスワード", max_length=50, min_length=8, 
                               widget=forms.PasswordInput,
                               error_messages={
                                   'required':'パスワードを入力してください',
                                   'invalid':'パスワードは半角英数字8字以上50字以下で入力してください',
                               },
                               validators=[
                                   RegexValidator(
                                       regex=r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
                                       message='パスワードは半角英数字両方含めてください'
                                   )
                               ])


class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('profile_image','username','bio','email')
        labels = {'profile_image':'プロフィール画像',
                  'username':'アカウント名',
                  'bio':'自己紹介',
                  'email':'メールアドレス'
                  }
        required = {
            'profile_image':False, 'bio':False,
        }
        
        
class PasswordChangeForm(forms.ModelForm):
    old_password = forms.CharField(
        label='元のパスワード', widget = forms.PasswordInput
    )
    new_password1 = forms.CharField(label='新しいパスワード', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,error_messages={
                                   'invalid':'パスワードは半角英数字8字以上50字以下で入力してください',
                               },
                               validators=[
                                   RegexValidator(
                                       regex=r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
                                       message='パスワードは半角英数字両方含めてください'
                                   )])
    new_password2 = forms.CharField(label='新しいパスワード(再入力)', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,)
    
    class Meta:
        model = User
        fields = ()
        
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if not self.instance.check_password(old_password):
            raise ValidationError('元のパスワードが違います')
        if new_password1 != new_password2:
            raise ValidationError('新しいパスワードが一致しません')
        
    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('new_password1'))
        user.save()
        return user
    
    
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="メールアドレス",
        required=True,
        error_messages={
            'required':'メールアドレスを入力してください',
            'invalid':'正しいメールアドレスの形式で入力してください'
        }
    )
    
    
class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {'password_mismatch':'パスワードが一致していません。'}
    
    new_password1 = forms.CharField(label='新しいパスワード', max_length=50, min_length=8, 
                               widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='新しいパスワード(再入力)', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,)
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        if not password:
            raise ValidationError('パスワードを入力してください。')
        
        if len(password) < 8 or len(password) > 50:
            raise ValidationError('パスワードは8字以上50字以下で入力してください。')
        
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',password):
            raise ValidationError('パスワードは半角英数字両方含めてください')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        return cleaned_data
        