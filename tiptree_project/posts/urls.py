from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create_post', views.create_post, name = 'create_post'),
    path('confirm', views.confirm, name = 'confirm'),
    path('edit_post/<int:post_id>', views.edit_post, name = 'edit_post'),
    path("<int:post_id>/save/", views.toggle_save, name="toggle_save"),
    path('saved', views.saved_post_list, name = 'saved_post_list'),
    path("<int:post_id>/help/", views.toggle_help, name="toggle_help"),
    path('helped', views.helped_post_list, name = 'helped_post_list'),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    path("<int:post_id>/delete/", views.post_delete, name="post_delete"),
]
