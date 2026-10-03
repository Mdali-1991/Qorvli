from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "first_name", "last_name", "location", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("QORVLI Profile", {"fields": ("bio", "profile_picture", "location")}),
    )
