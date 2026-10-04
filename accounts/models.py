"""Data model for QORVLI users."""

from urllib.parse import quote

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """Custom user model: Django's AbstractUser plus social profile fields."""

    bio = models.TextField(max_length=280, blank=True, default="")
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True, default=""
    )
    location = models.CharField(max_length=100, blank=True, default="")
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        """Show the username in the admin and shell."""
        return self.username

    def get_absolute_url(self):
        """URL of this user's public profile page."""
        return reverse("accounts:profile", kwargs={"username": self.username})

    @property
    def profile_picture_url(self):
        """Uploaded picture if set, otherwise a generated initials avatar."""
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return (
            "https://ui-avatars.com/api/?name="
            + quote(self.username)
            + "&background=6C5CE7&color=fff&size=256"
        )

    @property
    def post_count(self):
        """Number of posts this user has published."""
        return self.posts.count()
