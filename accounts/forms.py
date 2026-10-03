from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control qorvli-input", "placeholder": "you@example.com"}
        ),
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control qorvli-input", "placeholder": "First name"}
        ),
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control qorvli-input", "placeholder": "Last name"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control qorvli-input", "placeholder": "Choose a username"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control qorvli-input", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control qorvli-input", "placeholder": "Confirm password"}
        )

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control qorvli-input",
                "placeholder": "Username",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control qorvli-input", "placeholder": "Password"}
        )
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "bio", "location", "profile_picture")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control qorvli-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-control qorvli-input"}),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control qorvli-input",
                    "rows": 3,
                    "maxlength": 280,
                    "placeholder": "Tell the world about yourself (280 characters max)",
                }
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control qorvli-input", "placeholder": "City, Country"}
            ),
            "profile_picture": forms.ClearableFileInput(
                attrs={"class": "form-control qorvli-input", "accept": "image/*"}
            ),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get("bio", "")
        if len(bio) > 280:
            raise ValidationError("Bio cannot exceed 280 characters.")
        return bio

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")
        if picture and hasattr(picture, "size"):
            max_size_mb = 5
            if picture.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f"Image file too large ( > {max_size_mb}MB ).")
        return picture
