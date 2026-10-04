"""Views for the feed and for creating, editing and deleting posts
and comments.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods

from .forms import PostForm, CommentForm
from .models import Post, Comment, Like

User = get_user_model()


def form_error_text(form):
    """Join a bound form's errors into one sentence for a flash message."""
    return " ".join(
        error for errors in form.errors.values() for error in errors
    )


@login_required
@require_http_methods(["GET"])
def feed_view(request):
    """Paginated feed of all posts, optionally filtered by a search query."""
    query = request.GET.get("q", "").strip()
    posts = (
        Post.objects.select_related("author")
        .prefetch_related("likes", "comments__author")
        .annotate(
            is_liked=Exists(
                Like.objects.filter(post=OuterRef("pk"), user=request.user)
            )
        )
        .order_by("-created_at")
    )

    if query:
        posts = posts.filter(
            Q(content__icontains=query)
            | Q(author__username__icontains=query)
            | Q(author__first_name__icontains=query)
            | Q(author__last_name__icontains=query)
        ).distinct()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Distinct id prefixes so the composer and the comment inputs don't both
    # render id="id_content" (duplicate ids are invalid HTML).
    post_form = PostForm(auto_id="id_post_%s")

    context = {
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "post_form": post_form,
        "query": query,
        "suggested_users": User.objects.exclude(pk=request.user.pk).order_by(
            "-date_joined"
        )[:5],
    }
    return render(request, "posts/feed.html", context)


@login_required
@require_POST
def create_post_view(request):
    """Publish a new post for the signed-in user."""
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post has been published.")
    else:
        messages.error(
            request, f"Could not publish your post. {form_error_text(form)}"
        )
    return redirect("posts:feed")


@login_required
@require_http_methods(["GET", "POST"])
def edit_post_view(request, pk):
    """Edit a post. Only its author may do this."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        raise PermissionDenied("You do not have permission to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Your post has been updated.")
            return redirect(post)
        messages.error(request, "Please correct the errors below.")
    else:
        form = PostForm(instance=post)

    return render(
        request, "posts/edit_post.html", {"form": form, "post": post}
    )


@login_required
@require_POST
def delete_post_view(request, pk):
    """Delete a post. Only its author may do this."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        raise PermissionDenied(
            "You do not have permission to delete this post."
        )
    post.delete()
    messages.success(request, "Your post has been deleted.")
    return redirect("posts:feed")


@login_required
@require_POST
def add_comment_view(request, pk):
    """Add a comment to a post."""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Your comment has been added.")
    else:
        messages.error(
            request, f"Comment could not be added. {form_error_text(form)}"
        )
    return redirect(post)


@login_required
@require_POST
def delete_comment_view(request, pk):
    """Delete a comment. Allowed for its author or the post's author."""
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user and comment.post.author != request.user:
        raise PermissionDenied(
            "You do not have permission to delete this comment."
        )
    post = comment.post
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect(post)


@login_required
@require_POST
def toggle_like_view(request, pk):
    """AJAX endpoint: toggle a like on a post and return the new state."""
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse(
        {
            "liked": liked,
            "like_count": post.like_count,
            "post_id": post.pk,
        }
    )
