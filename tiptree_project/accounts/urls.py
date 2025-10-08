from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('regist', views.regist, name = 'regist'),
    path('confirm', views.confirm, name = 'confirm'),
    path('login', views.login_view, name = 'login'),
    path('logout', views.logout_view, name = 'logout'),
    path('help', views.help, name = 'help'),
    path('my_page', views.my_page, name = 'my_page'),
]
