"""App configuration for the posts app."""
from django.apps import AppConfig


class PostsConfig(AppConfig):
    """Registers the posts app (posts, comments and likes)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "posts"
    verbose_name = "Posts"
