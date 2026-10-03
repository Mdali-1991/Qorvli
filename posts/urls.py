"""URL routes for the feed, posts, comments and likes."""
from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("", views.feed_view, name="feed"),
    path("post/create/", views.create_post_view, name="create_post"),
    path("post/<int:pk>/edit/", views.edit_post_view, name="edit_post"),
    path("post/<int:pk>/delete/", views.delete_post_view, name="delete_post"),
    path("post/<int:pk>/comment/", views.add_comment_view, name="add_comment"),
    path("comment/<int:pk>/delete/", views.delete_comment_view, name="delete_comment"),
    path("post/<int:pk>/like/", views.toggle_like_view, name="toggle_like"),
]
