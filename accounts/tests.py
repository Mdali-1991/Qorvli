"""
Automated tests for the accounts app.

Run with:  python manage.py test accounts
"""

from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import User


class SignUpTests(TestCase):
    """Registration: validation, duplicates, reserved names and redirects."""

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
        self.assertEqual(
            response.status_code, 200
        )  # form redisplayed with error
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_signup_rejects_reserved_username(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "Edit",
                "first_name": "A",
                "last_name": "B",
                "email": "edit@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This username is reserved")
        self.assertFalse(User.objects.filter(username__iexact="edit").exists())

    def test_signup_redirects_logged_in_user_to_feed(self):
        User.objects.create_user(username="member", password="pass12345")
        self.client.login(username="member", password="pass12345")
        response = self.client.get(reverse("accounts:signup"))
        self.assertRedirects(response, reverse("posts:feed"))


class LoginLogoutTests(TestCase):
    """Logging in and out, including redirect safety."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser", password="pass12345"
        )

    def test_login_with_correct_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "loginuser", "password": "pass12345"},
        )
        self.assertRedirects(response, reverse("posts:feed"))

    def test_login_with_wrong_password_shows_error(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "loginuser", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_login_ignores_external_next_url(self):
        response = self.client.post(
            reverse("accounts:login") + "?next=https://evil.example.com/",
            {"username": "loginuser", "password": "pass12345"},
        )
        self.assertRedirects(response, reverse("posts:feed"))

    def test_login_follows_internal_next_url(self):
        target = reverse("accounts:profile", kwargs={"username": "loginuser"})
        response = self.client.post(
            reverse("accounts:login") + "?next=" + target,
            {"username": "loginuser", "password": "pass12345"},
        )
        self.assertRedirects(response, target)

    def test_logout_logs_user_out(self):
        self.client.login(username="loginuser", password="pass12345")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_rejects_get(self):
        self.client.login(username="loginuser", password="pass12345")
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    """Viewing and editing profiles."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="owner", password="pass12345"
        )
        self.other = User.objects.create_user(
            username="viewer", password="pass12345"
        )

    def test_profile_requires_login(self):
        response = self.client.get(
            reverse("accounts:profile", kwargs={"username": "owner"})
        )
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_profile_page_loads_for_logged_in_user(self):
        self.client.login(username="viewer", password="pass12345")
        response = self.client.get(
            reverse("accounts:profile", kwargs={"username": "owner"})
        )
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
        self.assertRedirects(
            response, reverse("accounts:profile", kwargs={"username": "owner"})
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Hello world")

    def test_edit_profile_page_loads(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("accounts:edit_profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_picture_fallback_url_is_generated(self):
        self.assertIn("ui-avatars.com", self.user.profile_picture_url)


class EnsureSuperuserCommandTests(TestCase):
    """The deploy-time command that creates the admin account."""

    env = {
        "DJANGO_SUPERUSER_USERNAME": "siteadmin",
        "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
        "DJANGO_SUPERUSER_PASSWORD": "Adm1n-Pass-2026!",
    }

    def run_command(self):
        out = StringIO()
        call_command("ensure_superuser", stdout=out)
        return out.getvalue()

    def test_creates_superuser_from_environment(self):
        with mock.patch.dict("os.environ", self.env):
            output = self.run_command()
        admin = User.objects.get(username="siteadmin")
        self.assertTrue(admin.is_superuser and admin.is_staff)
        self.assertTrue(admin.check_password("Adm1n-Pass-2026!"))
        self.assertIn("created", output)

    def test_running_twice_does_not_fail_or_duplicate(self):
        with mock.patch.dict("os.environ", self.env):
            self.run_command()
            output = self.run_command()
        self.assertEqual(User.objects.filter(username="siteadmin").count(), 1)
        self.assertIn("already exists", output)

    def test_skips_when_variables_missing(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            output = self.run_command()
        self.assertFalse(User.objects.exists())
        self.assertIn("skipping", output)


class AdminAccessTests(TestCase):
    """Only staff can reach the Django admin used for moderation (US14)."""

    def test_staff_can_manage_users_posts_comments_and_likes(self):
        User.objects.create_superuser(
            username="moderator", email="m@example.com", password="pw12345x"
        )
        self.client.login(username="moderator", password="pw12345x")
        for url in [
            "/admin/",
            "/admin/accounts/user/",
            "/admin/posts/post/",
            "/admin/posts/comment/",
            "/admin/posts/like/",
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_ordinary_member_is_refused(self):
        User.objects.create_user(username="member", password="pw12345x")
        self.client.login(username="member", password="pw12345x")
        response = self.client.get("/admin/posts/post/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
