from django.conf import settings
from django.db import models
from django.urls import reverse


class Post(models.Model):
    """A single post published by a user to the QORVLI feed."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["-created_at"], name="posts_post_created_at_idx")]

    def __str__(self):
        return f"Post #{self.pk} by {self.author.username}"

    def get_absolute_url(self):
        return reverse("posts:feed") + f"#post-{self.pk}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class Comment(models.Model):
    """A comment left by a user on a post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment #{self.pk} by {self.author.username} on Post #{self.post_id}"


class Like(models.Model):
    """A like relationship between a user and a post. Enforces one like per user per post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_like_per_user")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes Post #{self.post_id}"
