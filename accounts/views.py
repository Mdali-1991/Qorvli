from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import CreateView

from posts.models import Post, Like
from .forms import SignUpForm, LoginForm, ProfileUpdateForm
from .models import User


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        # A signed-in user has no reason to create another account.
        if request.user.is_authenticated:
            return redirect("posts:feed")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your QORVLI account has been created successfully. Please sign in.",
        )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below and try again.")
        return super().form_invalid(form)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("posts:feed")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                # Only follow ?next= if it points back to this site,
                # otherwise it could be used as an open redirect.
                next_url = request.GET.get("next")
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect("posts:feed")
            messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon!")
    return redirect("accounts:login")


@login_required
@require_http_methods(["GET"])
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = (
        Post.objects.filter(author=profile_user)
        .select_related("author")
        .prefetch_related("likes", "comments")
        .annotate(
            is_liked=Exists(
                Like.objects.filter(post=OuterRef("pk"), user=request.user)
            )
        )
        .order_by("-created_at")
    )
    context = {
        "profile_user": profile_user,
        "posts": posts,
        "is_own_profile": profile_user == request.user,
    }
    return render(request, "accounts/profile.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile", username=request.user.username)
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})
