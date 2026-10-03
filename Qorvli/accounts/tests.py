"""
Automated tests for the accounts app.

Run with:  python manage.py test accounts
"""
from django.test import TestCase
from django.urls import reverse

from .models import User


class SignUpTests(TestCase):
    def test_signup_page_loads(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing", email="dup@example.com", password="pass12345"
        )
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "another",
                "first_name": "A",
                "last_name": "B",
                "email": "dup@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)  # form redisplayed with error
        self.assertFalse(User.objects.filter(username="another").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="loginuser", password="pass12345")

    def test_login_with_correct_credentials(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "loginuser", "password": "pass12345"}
        )
        self.assertRedirects(response, reverse("posts:feed"))

    def test_login_with_wrong_password_shows_error(self):
        response = self.client.post(
            reverse("accounts:login"), {"username": "loginuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_logout_requires_login_first(self):
        self.client.login(username="loginuser", password="pass12345")
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="pass12345")
        self.other = User.objects.create_user(username="viewer", password="pass12345")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile", kwargs={"username": "owner"}))
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_profile_page_loads_for_logged_in_user(self):
        self.client.login(username="viewer", password="pass12345")
        response = self.client.get(reverse("accounts:profile", kwargs={"username": "owner"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "owner")

    def test_edit_profile_updates_bio(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("accounts:edit_profile"),
            {
                "first_name": "Owner",
                "last_name": "User",
                "bio": "Hello world",
                "location": "Dhaka",
            },
        )
        self.assertRedirects(response, reverse("accounts:profile", kwargs={"username": "owner"}))
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Hello world")

    def test_profile_picture_fallback_url_is_generated(self):
        self.assertIn("ui-avatars.com", self.user.profile_picture_url)
