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
    path("<int:post_id>/comment/", views.comment_create, name="comment_create"),
    path("<int:post_id>/supplement/", views.supplement_create, name="supplement_create"),
    path("<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("supplement/<int:supplement_id>/supplement_reply/",views.supplement_reply,name="supplement_reply"),
    path("comment/<int:comment_id>/comment_reply/",views.comment_reply,name="comment_reply"),
    path("supplement/<int:supplement_id>/delete/",views.supplement_delete,name="supplement_delete"),
    path("supplement_reply/<int:supplement_reply_id>/delete/",views.supplement_reply_delete,name="supplement_reply_delete"),
    path("comment/<int:comment_id>/delete/",views.comment_delete,name="comment_delete"),
    path("comment_reply/<int:comment_reply_id>/delete/",views.comment_reply_delete,name="comment_reply_delete"),
]