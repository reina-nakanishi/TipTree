from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)

class UserManager(BaseUserManager):
    
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        if not username:
            raise ValueError('アカウント名を入力してください')
        if not password:
            raise ValueError('パスワードを入力してください')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_active'] = True
        extra_fields['is_superuser'] = True
        return self.create_user(email, username, password, **extra_fields)
        

class User(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=50,unique=True)
    profile_image = models.FileField(null=True)
    bio = models.TextField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uppdated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email' #このテーブルのレコードを一意に識別するフィールド
    REQUIRED_FIELDS = ['username'] #createsuperuserの時に入力を求められる
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table ='user'