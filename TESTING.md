# Testing — QORVLI

This document covers both the **automated test suite** and the **manual testing
procedure** carried out against the full-stack application, as required by
Learning Outcome 1.5 of the assessment.

## 1. Automated tests

Automated tests live in `accounts/tests.py` and `posts/tests.py` and cover
authentication, permissions and CRUD behaviour — the parts of the app where a
regression would be easy to introduce and hard to notice by eye.

Run them from the repository root (a `.env` with at least `SECRET_KEY` is
required, see `README.md` §7):

```bash
python manage.py test
flake8 .
python manage.py makemigrations --check --dry-run
```

| App | What is covered |
|---|---|
| `accounts` | Signup form validation (duplicate email rejected), login with correct/incorrect credentials, login ignores an external `?next=` URL but follows an internal one, logout works via POST and rejects GET (405), profile page requires login, edit-profile page loads and saving it updates the database, fallback avatar URL is generated when no picture is uploaded |
| `posts` | Feed requires login, search filters posts by content, creating a post with empty content is rejected, creating a post with valid content succeeds, only the post owner can edit/delete their post (custom 403 page for everyone else), comments can be added/rejected when empty, a comment can be deleted by its author **or** the post owner but not by an unrelated user, liking toggles a `Like` row on/off, the one-like-per-user database constraint is enforced |

31 tests, all passing (`python manage.py test`). `flake8` and `pycodestyle`
report no issues with the settings in `setup.cfg`, and
`python manage.py makemigrations --check` reports no pending model changes.

### Production-configuration check

Before deploying, the app was run locally with production settings
(`DEBUG=False`, `CLOUDINARY_URL` set) to mirror Heroku:

| Check | Command | Result |
|---|---|---|
| Django deployment checklist | `python manage.py check --deploy` | No issues (HSTS preload is deliberately off for a `herokuapp.com` domain and that check is silenced in `settings.py`) |
| Static files build | `python manage.py collectstatic --noinput` | 140 files copied, hashed manifest generated |
| Migrations | `python manage.py migrate` | All migrations applied |
| Production server | `gunicorn qorvli_project.wsgi` | Login page 200, `/static/css/style.css` 200 via WhiteNoise, unknown URL returns the custom 404 |

## 2. Manual test procedure

Manual testing followed the user journeys below on desktop Chrome, mobile
Chrome (DevTools device emulation) and keyboard-only navigation.

| # | Test case | Steps | Expected result | Result |
|---|---|---|---|---|
| 1 | Sign up | Go to `/accounts/signup/`, fill in a new username/email/password | Account created, redirected to login with a success message | Pass |
| 2 | Duplicate email blocked | Sign up again with an email already in use | Form re-displays with "An account with this email already exists." | Pass |
| 3 | Login (valid) | Enter correct username/password | Redirected to feed, "Welcome back" message shown | Pass |
| 4 | Login (invalid) | Enter wrong password | Form re-displays with "Invalid username or password." — no user is logged in | Pass |
| 5 | Logout | Click Logout (submits a POST form) | Session ends, redirected to login | Pass |
| 6 | Create post (text) | Type text in composer, click Post | Post appears at top of feed immediately | Pass |
| 7 | Create post (empty) | Submit composer with no text | Post rejected, error message shown, nothing added to feed | Pass |
| 8 | Create post with image | Attach a JPG under 8MB | Post is created with the image displayed inline | Pass |
| 9 | Oversized image rejected | Attach an image over 8MB | Form error: "Image file too large" | Pass |
| 10 | Edit own post | Open a post's "..." menu → Edit → change text → Save | Feed shows updated text | Pass |
| 11 | Delete own post | "..." menu → Delete → confirm in modal | Post removed from feed, confirmation message shown | Pass |
| 12 | Cannot edit/delete others' posts | Log in as a different user, try to visit another user's edit-post URL directly | Custom 403 page returned, post unchanged | Pass |
| 13 | Add comment | Open comments on a post, type a comment, submit | Comment appears under the post without a full page reload feel (redirect + anchor) | Pass |
| 14 | Delete comment (own) | Delete a comment you wrote | Comment removed | Pass |
| 15 | Delete comment (as post owner) | Delete someone else's comment on your own post | Comment removed | Pass |
| 16 | Cannot delete unrelated comment | Try to delete a comment that isn't yours and isn't on your post (via direct POST) | 403 Forbidden | Pass |
| 17 | Like / unlike | Click the heart icon on a post | Icon fills in, counter increments; clicking again reverses it — no page reload (AJAX) | Pass |
| 18 | Search | Type a keyword into the navbar search | Feed filters to posts/authors matching the keyword, "Clear" link resets it | Pass |
| 19 | Pagination | Create 11+ posts, scroll to bottom | Pagination controls appear and page through correctly | Pass |
| 20 | Edit profile | Update bio, location and profile picture | Profile page reflects the new details and avatar immediately | Pass |
| 21 | View another user's profile | Click a username/avatar | Their profile and posts load; "Edit Profile" button is hidden (not their own profile) | Pass |
| 22 | 404 handling | Visit a non-existent URL | Custom 404 page shown, no stack trace | Pass |
| 23 | Broken/forward navigation | Use browser Back/Forward after liking/commenting | Page state is still correct, no broken links or console errors | Pass |
| 24 | Keyboard navigation | Tab through navbar, composer, like/comment buttons, modals | All interactive elements are reachable and usable via keyboard; focus is visible | Pass |
| 25 | Screen reader labels | Inspect like/comment/delete buttons with a screen reader | Icon-only buttons announce their purpose (`aria-label`) rather than reading nothing | Pass |
| 26 | Responsive layout | Resize viewport from desktop to mobile widths | Navbar collapses to a hamburger menu, sidebar hides on small screens, cards remain readable | Pass |
| 27 | Secrets not exposed | Inspect repository and deployed source | No password or `SECRET_KEY` committed; `.env` is git-ignored; `DEBUG=False` in production | Pass |

## 3. Bugs found during testing and their fixes

| Bug | Found during | Fix |
|---|---|---|
| Comment "aria-expanded" state on the comment-toggle button never updated when using the Bootstrap collapse, so screen readers always announced it as collapsed. | Test 25 | Added `shown.bs.collapse` / `hidden.bs.collapse` listeners in `main.js` that flip `aria-expanded` on the toggle button. |
| Icon-only buttons (like, comment toggle, delete comment, "..." menu) had no accessible name. | Test 25 | Added explicit `aria-label` attributes and `aria-hidden="true"` on the decorative icons across `feed.html`, `profile.html` and `base.html`. |
| Forms gave no visual feedback between click and page response, so a slow connection made it look like nothing happened. | Test 6, 20 | Added a shared `initSubmitSpinners()` handler in `main.js` that disables the submit button and shows a spinner label while any form is submitting. |
| Missing database migrations meant the project could not be migrated on a clean checkout. | Test 1 (initial setup) | Generated and committed `accounts/migrations/0001_initial.py` and `posts/migrations/0001_initial.py`. |
| The like button's filled/unfilled state used an invalid template expression (`{% if post.is_liked_by:request.user %}`), which Django cannot resolve — so a post you had already liked still rendered with an empty heart after a page reload, even though the `Like` row existed in the database. | Test 17, re-checked after a page refresh | Annotated the `Post` queryset in `feed_view` and `profile_view` with `is_liked = Exists(Like.objects.filter(post=OuterRef("pk"), user=request.user))` and updated the templates to use `post.is_liked`, so the correct state is calculated in the database query instead of an unsupported template lookup. |

| The "Edit Profile" page always returned 404. `profile/<str:username>/` was listed before `profile/edit/` in `accounts/urls.py`, so "edit" was treated as a username. | Code review / automated test `test_edit_profile_updates_bio` | Moved `profile/edit/` above the username pattern. |
| The automated test suite errored on a clean checkout (`Missing staticfiles manifest entry`) because the manifest static storage needs `collectstatic`. | Running `python manage.py test` on a fresh clone | Tests now use Django's plain `StaticFilesStorage` (`settings.py`). |
| Open redirect: after login, any `?next=` URL was followed, including external sites. | Security review | `login_view` now checks `url_has_allowed_host_and_scheme` before redirecting. |
| Logout worked over GET, so any page could log a user out with a link or image. | Security review | `logout_view` is `@require_POST`; the navbar uses a small form with a CSRF token. |
| The composer and every comment box rendered `id="id_content"`, giving duplicate ids (invalid HTML) and unlabelled inputs. | HTML validation | Composer uses `auto_id="id_post_%s"`; each comment input has a unique id and a visually hidden `<label>`. |
| The composer placeholder showed the literal text `{{ user }}`. | Manual test 6 | Placeholder changed to "What's happening?" (template tags are not rendered inside Python strings). |
| The photo input was `display: none`, so keyboard users could not attach an image; picking a file wrote the filename into the icon element. | Test 24 | Input is now visually hidden but focusable, with a focus ring on its label; the filename goes into a dedicated `<span>`. |
| The like button's `aria-pressed` / `aria-label` didn't change after an AJAX toggle. | Test 25 | `main.js` updates both attributes from the JSON response. |
| `makemigrations --check` found pending changes (primary-key type on `User`, index name on `Post`). | Code review | Added `accounts/migrations/0002_alter_user_id.py`; gave the `Post` index an explicit name matching the existing migration. |

| Heroku could not detect the app because `Procfile` and `requirements.txt` were inside a `Qorvli/` subfolder rather than the repository root. | Deployment review | Moved the whole project to the repository root and added `.python-version` (3.11). |

## 4. Validation

Fill in after deployment, with screenshots in `docs/`:

| Tool | Pages / files | Result |
|---|---|---|
| [W3C HTML validator](https://validator.w3.org/) (check by URI, or paste "view source" for logged-in pages) | Login, Sign up, Feed, Profile, Edit profile, Edit post, 404 | _to record_ |
| [W3C CSS validator (Jigsaw)](https://jigsaw.w3.org/css-validator/) | `static/css/style.css` | _to record_ |
| [JSHint](https://jshint.com/) (`esversion: 6`) | `static/js/main.js` | _to record_ |
| [CI Python Linter](https://pep8ci.herokuapp.com/) / `flake8` | All `.py` files | `flake8 .`: no issues |
| Lighthouse (Chrome DevTools) | Feed, Profile (desktop + mobile) | _to record_ |

No known bugs remain unfixed at the time of submission.
