from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス",
                             error_messages={
                                 'invalid' : '有効なメールアドレスを入力してください'
                             })
    password = forms.CharField(label="パスワード", max_length=50, min_length=8, 
                               widget=forms.PasswordInput,
                               error_messages={
                                   'invalid':'パスワードは半角英数字8字以上50字以下で入力してください',
                               },
                               validators=[
                                   RegexValidator(
                                       regex=r'^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]+$',
                                       message='パスワードは半角英数字両方含めてください'
                                   )
                               ])