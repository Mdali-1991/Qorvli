# QORVLI

A full-stack, database-backed social media web application built with
**Python, Django, PostgreSQL, HTML/CSS (Bootstrap 5) and JavaScript**. Users
can create an account, build a profile, publish posts with images, like and
comment on other users' posts, and search the feed — all backed by a
relational database with full CRUD functionality.

Live demo: _add your deployed Heroku/Render URL here once deployed_

---

## 1. Purpose & rationale

Most people want a simple, distraction-free way to share short updates and
photos with a community, and to see and respond to what others are posting,
without the noise of ads, algorithmic ranking or a huge feature surface.

**Target audience:** small communities, clubs, cohorts or friend groups (e.g.
a university course, a hobby group, a local sports club) who want a private
space to post updates, share photos and discuss them, without setting up a
full commercial social network.

**What QORVLI provides:**
- A personal profile with a bio, location and profile picture
- A chronological feed of posts from everyone on the platform
- The ability to create, edit and delete your own posts (with optional images)
- Comments and likes on any post, with instant feedback
- Keyword search across post content and author names
- A clean, responsive, accessible interface that works on desktop and mobile

The project is intentionally scoped around one core loop — **post, like,
comment, discover** — done well and tested thoroughly, rather than a wide
set of half-finished features. This keeps the codebase robust and the data
model easy to reason about, in line with what the CRUD/data-modelling
criteria for this unit are assessing.

---

## 2. Features

| Feature | Where |
|---|---|
| Sign up / log in / log out | `accounts` app |
| Custom user profile (bio, location, profile picture, avatar fallback) | `accounts` app |
| View any user's profile and their posts | `accounts` app |
| Create / edit / delete posts (text + optional image) | `posts` app |
| Comment on posts, delete your own comment (or any comment on your post) | `posts` app |
| Like / unlike a post via AJAX (no page reload) | `posts` app, `main.js` |
| Search posts by content or author | `posts` app |
| Pagination of the feed | `posts` app |
| Custom 403 / 404 / 500 error pages | `templates/`, `qorvli_project/views.py` |
| Flash messages for every user action (success/error/info) | `base.html` |

---

## 3. Data model / schema

The application uses two Django apps, sharing one PostgreSQL database.

```mermaid
erDiagram
    USER ||--o{ POST : writes
    USER ||--o{ COMMENT : writes
    USER ||--o{ LIKE : gives
    POST ||--o{ COMMENT : has
    POST ||--o{ LIKE : has

    USER {
        bigint id PK
        string username
        string email
        string first_name
        string last_name
        text bio
        string location
        image profile_picture
        datetime date_joined
    }
    POST {
        bigint id PK
        bigint author_id FK
        text content
        image image
        datetime created_at
        datetime updated_at
    }
    COMMENT {
        bigint id PK
        bigint post_id FK
        bigint author_id FK
        string content
        datetime created_at
    }
    LIKE {
        bigint id PK
        bigint post_id FK
        bigint user_id FK
        datetime created_at
    }
```

**Relationships**
- A `User` can author many `Post`s, `Comment`s and `Like`s (one-to-many).
- A `Post` can have many `Comment`s and many `Like`s (one-to-many).
- `Like` has a **unique constraint on `(post, user)`** so a user can only
  like a given post once — enforced at the database level, not just in the
  UI.
- `Comment` and `Like` both `CASCADE` delete when their parent `Post` or
  `User` is deleted, so there is never an orphaned row.

See `accounts/models.py` and `posts/models.py` for the full field
definitions, and `accounts/migrations/0001_initial.py` /
`posts/migrations/0001_initial.py` for the exact database schema that gets
created.

---

## 4. UX design process

Wireframes for the main screens are included in
[`docs/wireframes/`](docs/wireframes/) and were sketched before
implementation to plan information hierarchy and navigation:

- [`01-feed-wireframe.svg`](docs/wireframes/01-feed-wireframe.svg) — navbar
  with search, a post composer, a scrollable list of post cards (each with
  like/comment actions), and a "suggested users" sidebar on wide screens.
- [`02-profile-wireframe.svg`](docs/wireframes/02-profile-wireframe.svg) —
  profile banner, avatar, bio/meta information, an edit button (only visible
  to the profile owner), and that user's own posts below.
- [`03-auth-wireframe.svg`](docs/wireframes/03-auth-wireframe.svg) — login
  and sign-up screens side by side, showing field layout and where inline
  validation errors appear.
- [`04-mobile-responsive-wireframe.svg`](docs/wireframes/04-mobile-responsive-wireframe.svg) —
  how the feed collapses to a single column with a hamburger menu below the
  992px breakpoint.

Design decisions driven by UX/accessibility principles:
- **Information hierarchy:** semantic HTML (`<nav>`, `<main>`, `<footer>`,
  heading levels) is used throughout so structure is conveyed to assistive
  technology, not just visually.
- **User control:** likes/comments give instant feedback (AJAX, animated
  heart, live counters); form submissions show a spinner + "Saving..." state
  so the user always knows an action registered; deleting a post or comment
  always asks for confirmation in a modal first.
- **Consistency:** all cards, buttons and form inputs reuse the same
  `qorvli-*` component classes, so interaction patterns don't change between
  the feed and the profile page.
- **Accessibility:** icon-only buttons (like, comment, delete, menu, search)
  have explicit `aria-label`s, decorative icons are `aria-hidden`, the
  comment-toggle's `aria-expanded` state is kept in sync with the collapse
  animation, and flash messages are announced via `aria-live="polite"`.
- **No dead ends:** unknown URLs are handled by a custom, on-brand 404 page
  rather than Django's default debug page, and attempts to change another
  user's content get a custom 403 page.
- **Forms:** every input has a programmatically associated `<label>`
  (visually hidden where the design shows only a placeholder), each page has
  a single `<h1>`, and delete-confirmation modals are labelled with
  `aria-labelledby`.

---

## 5. Security

- `SECRET_KEY`, `DATABASE_URL` and all other secrets are read from
  environment variables via `django-environ` and are **never** committed —
  `.env` is listed in `.gitignore`, and `.env.example` is provided as a
  template with placeholder values only.
- `DEBUG` defaults to `False` and must be explicitly enabled in a local
  `.env` file; it is never `True` in production.
- When `DEBUG=False`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE` and
  `CSRF_COOKIE_SECURE` are all enabled automatically.
- `SECURE_CONTENT_TYPE_NOSNIFF` and `X_FRAME_OPTIONS = "DENY"` are set to
  reduce MIME-sniffing and clickjacking risk.
- Every view that modifies data is protected by `@login_required` and/or
  `@require_POST`/`@require_http_methods`, and Django's CSRF protection is
  applied to every form.
- **Object-level permission checks** are enforced in the view layer, not
  just hidden in the template: only a post's author can edit/delete it, and
  only a comment's author *or* the post's author can delete a comment
  (verified in `posts/tests.py`). Denied requests raise `PermissionDenied`,
  which renders the custom `403.html` page.
- The login view only follows a `?next=` URL if it points back to this site
  (`url_has_allowed_host_and_scheme`), preventing open-redirect phishing.
- Logout only accepts `POST` (with a CSRF token), so another site cannot log
  a user out with a hidden link or image.
- `SECURE_HSTS_SECONDS` (default 1 hour, configurable) and
  `SECURE_PROXY_SSL_HEADER` are set in production so HTTPS is enforced
  correctly behind Heroku's router.
- Passwords are validated with Django's built-in password validators
  (minimum length, similarity to user attributes, common-password and
  fully-numeric checks) and stored using Django's salted-hash algorithm —
  never in plain text.

---

## 6. Testing

Full testing procedure, automated test coverage and a log of bugs found and
fixed during development is documented in [`TESTING.md`](TESTING.md).

Quick start:

```bash
python manage.py test
pycodestyle .        # Python style, configured in setup.cfg
```

**Code style:** Python follows PEP8 with one explicit exception: the maximum
line length is 100 characters instead of 79 (set in `setup.cfg`), and
auto-generated `migrations/` are excluded.

---

## 7. Local setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env with your own SECRET_KEY / DATABASE_URL

# Create the Postgres database (adjust to your local Postgres setup)
createdb qorvli_db

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/signup/` to create an account, then
`http://127.0.0.1:8000/` for the feed.

Media (uploaded images) are saved to the local `media/` folder in
development. In production the filesystem is ephemeral, so set the
`CLOUDINARY_URL` environment variable (free Cloudinary account) and uploads
are stored there instead (see `qorvli_project/settings.py`).

---

## 8. Deploying to Heroku

```bash
heroku login
heroku create qorvli-app
heroku addons:create heroku-postgresql:essential-0
heroku config:set SECRET_KEY="your-production-secret-key"
heroku config:set DEBUG=False
heroku config:set CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
heroku config:set ALLOWED_HOSTS=qorvli-app.herokuapp.com
heroku config:set CSRF_TRUSTED_ORIGINS=https://qorvli-app.herokuapp.com

git push heroku main

heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku open
```

`Procfile` already defines the `release` (runs migrations automatically on
every deploy) and `web` (Gunicorn) processes. Static files are served via
WhiteNoise (`STORAGES["staticfiles"]` in `settings.py`), so no extra
buildpack configuration is needed.

After deploying, test that the deployed version matches the development
version (same features, same data model) — see Test #1–27 in `TESTING.md`.

---

## 9. Project structure

```
qorvli_project/     # Django project settings, root URLs, error handlers
accounts/            # Custom User model, signup/login/profile views
posts/               # Post, Comment, Like models and views
templates/           # Shared base template + 404/500 pages
static/              # Custom CSS and JavaScript (no external local files needed)
docs/wireframes/      # UX wireframes produced during the design phase
TESTING.md           # Manual + automated testing procedure and results
```

---

## 10. Attribution

- Built with [Django](https://www.djangoproject.com/) and
  [Bootstrap 5](https://getbootstrap.com/) (loaded via CDN, see
  `templates/base.html`) plus [Bootstrap Icons](https://icons.getbootstrap.com/).
- Fonts: [Poppins and Inter](https://fonts.google.com/) via Google Fonts
  (`templates/base.html`).
- Fallback avatars generated via [ui-avatars.com](https://ui-avatars.com/)
  when a user has not uploaded a profile picture (`accounts/models.py`).
- `getCookie()` in `static/js/main.js` is taken from the
  [Django CSRF documentation](https://docs.djangoproject.com/en/5.0/howto/csrf/)
  (credited in a comment above the function).
- Image hosting in production: [Cloudinary](https://cloudinary.com/) via
  `django-cloudinary-storage`; static files served by
  [WhiteNoise](https://whitenoise.readthedocs.io/).
- Apart from the items above, all application code (models, views, forms,
  templates, custom CSS/JS) was written for this project; no walkthrough
  project code was copied.
