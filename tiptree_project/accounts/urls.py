from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView,CustomPasswordResetDoneView,CustomPasswordResetConfirmView

app_name = 'accounts'

urlpatterns = [
    path('regist', views.regist, name = 'regist'),
    path('confirm', views.confirm, name = 'confirm'),
    path('login', views.login_view, name = 'login'),
    path('logout', views.logout_view, name = 'logout'),
    path('password_reset', CustomPasswordResetView.as_view(), name='password_reset'), 
    path('password_reset/done', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('my_page', views.my_page, name = 'my_page'),
    path('user_edit', views.user_edit, name = 'user_edit'),
    path('change_password', views.change_password, name = 'change_password'),
]
