from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User
from django.contrib.auth import get_user_model


User = get_user_model

class RegistForm(forms.Modelform):
    password1 = forms.CharField(lavel='パスワード', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,error_messages={
                                   'invalid':'パスワードは半角英数字8字以上50字以下で入力してください',
                               },
                               validators=[
                                   RegexValidator(
                                       regex=r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
                                       message='パスワードは半角英数字両方含めてください'
                                   )])
    password2 = forms.CharField(lavel='パスワード再入力', max_length=50, min_length=8, 
                               widget=forms.PasswordInput,)
    
    class Meta:
        model = User
        fields = ('username','email')
            
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
