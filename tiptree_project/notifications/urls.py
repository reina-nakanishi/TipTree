from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("<int:notification_id>/",views.notification_redirect,name="redirect"),
]