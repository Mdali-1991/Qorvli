from django import forms
from django.core.exceptions import ValidationError

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("content", "image")
        error_messages = {"content": {"required": "Your post cannot be empty."}}
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control qorvli-input qorvli-textarea",
                    "rows": 3,
                    "maxlength": 2000,
                    "placeholder": "What's happening?",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control qorvli-input", "accept": "image/*"}
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise ValidationError("Your post cannot be empty.")
        if len(content) > 2000:
            raise ValidationError("Your post cannot exceed 2000 characters.")
        return content

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size"):
            max_size_mb = 8
            if image.size > max_size_mb * 1024 * 1024:
                raise ValidationError(f"Image file too large ( > {max_size_mb}MB ).")
        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        error_messages = {"content": {"required": "Comment cannot be empty."}}
        widgets = {
            "content": forms.TextInput(
                attrs={
                    "class": "form-control qorvli-input qorvli-comment-input",
                    "placeholder": "Write a comment...",
                    "maxlength": 500,
                    "autocomplete": "off",
                }
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise ValidationError("Comment cannot be empty.")
        return content
