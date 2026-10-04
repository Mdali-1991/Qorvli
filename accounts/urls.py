"""URL routes for authentication and profiles, mounted at /accounts/."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # "profile/edit/" must come before "profile/<str:username>/", otherwise
    # the username pattern captures "edit" and the edit page is unreachable.
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path("profile/<str:username>/", views.profile_view, name="profile"),
]
