"""
Automated tests for the posts app (CRUD, comments, likes).

Run with:  python manage.py test posts
"""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Comment, Like, Post


class FeedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.client.login(username="alice", password="pass12345")

    def test_feed_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("posts:feed"))
        self.assertEqual(response.status_code, 302)

    def test_feed_loads_for_logged_in_user(self):
        response = self.client.get(reverse("posts:feed"))
        self.assertEqual(response.status_code, 200)

    def test_feed_search_filters_by_content(self):
        Post.objects.create(author=self.user, content="Learning Django is great")
        Post.objects.create(author=self.user, content="Something unrelated")
        response = self.client.get(reverse("posts:feed"), {"q": "Django"})
        self.assertContains(response, "Learning Django is great")
        self.assertNotContains(response, "Something unrelated")


class PostCRUDTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.other = User.objects.create_user(username="intruder", password="pass12345")

    def test_create_post_requires_content(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("posts:create_post"), {"content": ""})
        self.assertRedirects(response, reverse("posts:feed"))
        self.assertEqual(Post.objects.count(), 0)

    def test_create_post_success(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("posts:create_post"), {"content": "My first post"})
        self.assertRedirects(response, reverse("posts:feed"))
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().author, self.owner)

    def test_owner_can_edit_own_post(self):
        post = Post.objects.create(author=self.owner, content="Original")
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(
            reverse("posts:edit_post", kwargs={"pk": post.pk}), {"content": "Updated"}
        )
        self.assertRedirects(response, reverse("posts:feed"))
        post.refresh_from_db()
        self.assertEqual(post.content, "Updated")

    def test_non_owner_cannot_edit_post(self):
        post = Post.objects.create(author=self.owner, content="Original")
        self.client.login(username="intruder", password="pass12345")
        response = self.client.post(
            reverse("posts:edit_post", kwargs={"pk": post.pk}), {"content": "Hacked"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        post.refresh_from_db()
        self.assertEqual(post.content, "Original")

    def test_owner_can_delete_own_post(self):
        post = Post.objects.create(author=self.owner, content="Delete me")
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("posts:delete_post", kwargs={"pk": post.pk}))
        self.assertRedirects(response, reverse("posts:feed"))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_non_owner_cannot_delete_post(self):
        post = Post.objects.create(author=self.owner, content="Keep me")
        self.client.login(username="intruder", password="pass12345")
        response = self.client.post(reverse("posts:delete_post", kwargs={"pk": post.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())


class CommentTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.commenter = User.objects.create_user(username="commenter", password="pass12345")
        self.post = Post.objects.create(author=self.owner, content="Comment on this")

    def test_logged_in_user_can_comment(self):
        self.client.login(username="commenter", password="pass12345")
        response = self.client.post(
            reverse("posts:add_comment", kwargs={"pk": self.post.pk}), {"content": "Nice post!"}
        )
        self.assertRedirects(response, reverse("posts:feed"))
        self.assertEqual(Comment.objects.count(), 1)

    def test_empty_comment_is_rejected(self):
        self.client.login(username="commenter", password="pass12345")
        self.client.post(
            reverse("posts:add_comment", kwargs={"pk": self.post.pk}),
            {"content": "  "},
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_author_can_delete_own_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.commenter, content="Hi")
        self.client.login(username="commenter", password="pass12345")
        response = self.client.post(reverse("posts:delete_comment", kwargs={"pk": comment.pk}))
        self.assertRedirects(response, reverse("posts:feed"))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_post_owner_can_delete_others_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.commenter, content="Hi")
        self.client.login(username="owner", password="pass12345")
        response = self.client.post(reverse("posts:delete_comment", kwargs={"pk": comment.pk}))
        self.assertRedirects(response, reverse("posts:feed"))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_unrelated_user_cannot_delete_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.commenter, content="Hi")
        User.objects.create_user(username="stranger", password="pass12345")
        self.client.login(username="stranger", password="pass12345")
        response = self.client.post(reverse("posts:delete_comment", kwargs={"pk": comment.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())


class LikeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="liker", password="pass12345")
        self.author = User.objects.create_user(username="author", password="pass12345")
        self.post = Post.objects.create(author=self.author, content="Like this")
        self.client.login(username="liker", password="pass12345")

    def test_toggle_like_creates_like(self):
        response = self.client.post(reverse("posts:toggle_like", kwargs={"pk": self.post.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["liked"])
        self.assertEqual(data["like_count"], 1)
        self.assertEqual(Like.objects.count(), 1)

    def test_toggle_like_twice_removes_like(self):
        self.client.post(reverse("posts:toggle_like", kwargs={"pk": self.post.pk}))
        response = self.client.post(reverse("posts:toggle_like", kwargs={"pk": self.post.pk}))
        data = response.json()
        self.assertFalse(data["liked"])
        self.assertEqual(data["like_count"], 0)
        self.assertEqual(Like.objects.count(), 0)

    def test_duplicate_like_is_prevented_by_unique_constraint(self):
        Like.objects.create(post=self.post, user=self.user)
        with self.assertRaises(Exception):
            Like.objects.create(post=self.post, user=self.user)
