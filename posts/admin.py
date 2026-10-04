"""Django admin configuration for posts, comments and likes."""

from django.contrib import admin

from .models import Post, Comment, Like


class CommentInline(admin.TabularInline):
    """Show a post's comments on the post's admin page."""

    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post list with author, date and engagement counts."""

    list_display = (
        "id",
        "author",
        "created_at",
        "like_count",
        "comment_count",
    )
    search_fields = ("content", "author__username")
    list_filter = ("created_at",)
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Searchable list of comments."""

    list_display = ("id", "author", "post", "created_at")
    search_fields = ("content", "author__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """List of likes, mainly for moderation and debugging."""

    list_display = ("id", "user", "post", "created_at")
