# QORVLI

QORVLI is a small, private social network for clubs and community groups.
Members create a profile, share short updates and photos, comment on and
like each other's posts, and search everything that has been shared. It is
a full-stack Django application backed by a relational PostgreSQL database
with full create, read, update and delete (CRUD) functionality.

**Live site:** _add your Heroku URL here after deploying_

![QORVLI shown on a laptop (the feed) and a phone (a member's profile)](docs/screenshots/hero.png)

## Contents

1. [Purpose and rationale](#1-purpose-and-rationale)
2. [User stories](#2-user-stories)
3. [Features](#3-features)
4. [UX design](#4-ux-design)
5. [Data model](#5-data-model)
6. [Security](#6-security)
7. [Technologies used](#7-technologies-used)
8. [Testing](#8-testing)
9. [Local setup](#9-local-setup)
10. [Deploying to Heroku](#10-deploying-to-heroku)
11. [Project structure](#11-project-structure)
12. [Development process](#12-development-process)
13. [Attribution and credits](#13-attribution-and-credits)

---

## 1. Purpose and rationale

Small groups such as a walking club, a university cohort or a local sports
team usually coordinate through a mix of group chats and large commercial
social networks. Group chats bury useful posts (meeting points, lost
property, photos) under a stream of messages, and commercial networks add
ads, algorithmic ranking and far more features than a club needs.

**Target audience:** members of a single club or community group who want
one place to post updates, share photos and discuss them, plus the
organisers who need their announcements to be seen.

**What QORVLI provides:**
- A personal profile with a name, bio, location and profile picture.
- A chronological feed: the newest post is always at the top, with no
  ranking algorithm deciding what members see.
- Posts with optional photos that their author can edit or delete.
- Comments and likes for quick discussion and acknowledgement.
- Search across post text and member names, so older announcements can
  be found again.
- A responsive, accessible interface that works on phones and desktops.

The scope is deliberately focused on one core loop (**post, discuss,
find**) done thoroughly, with permission checks, validation, feedback
and tests on every action, rather than a wide set of half-finished
features.

---

## 2. User stories

| ID | As a... | I want to... | So that... |
|---|---|---|---|
| US01 | visitor | create an account with my name and email | I can join my club's space |
| US02 | member | log in and log out securely | my account can't be used by others |
| US03 | member | edit my profile (name, bio, location, picture) | other members know who I am |
| US04 | member | view another member's profile and posts | I can see what they have shared |
| US05 | member | publish a post with optional text and photo | I can share news and pictures |
| US06 | member | edit a post I wrote | I can fix mistakes or add details |
| US07 | member | delete a post I wrote, after confirming | I can remove things I no longer want shared |
| US08 | member | comment on any post | I can join the discussion |
| US09 | member | delete my own comments, and comments on my posts | I can moderate discussion of my posts |
| US10 | member | like and unlike posts without the page reloading | I can react quickly |
| US11 | member | search posts and members | I can find an old announcement or a person |
| US12 | member | get clear feedback after every action | I always know whether something worked |
| US13 | member | be sure nobody else can edit or delete my content | my posts stay as I wrote them |
| US14 | site owner | manage all users and content in an admin area | I can moderate the community |

How each story is met is tested in
[`TESTING.md`, section 3](TESTING.md#3-user-story-testing).

---

## 3. Features

| Feature | User stories | Where in the code |
|---|---|---|
| Sign up with validation (unique email, password rules, reserved usernames) | US01 | `accounts/forms.py`, `accounts/views.py` |
| Log in (safe `?next=` redirects) and POST-only log out | US02 | `accounts/views.py` |
| Profile page with avatar, bio, location, join date and post count | US03, US04 | `accounts/templates/accounts/profile.html` |
| Edit your own profile, including picture upload (5MB limit) | US03 | `accounts/views.py` (`edit_profile_view`) |
| Create posts with optional image (8MB limit) | US05 | `posts/views.py` (`create_post_view`) |
| Edit and delete your own posts; delete asks for confirmation | US06, US07, US13 | `posts/views.py`, `feed.html` modals |
| Comment on posts; delete own comments or comments on your post | US08, US09 | `posts/views.py` |
| Like/unlike via AJAX with live counter | US10 | `toggle_like_view`, `static/js/main.js` |
| Search posts and members, with paginated results | US11 | `feed_view` |
| Flash messages for every action, spinners while forms submit | US12 | `templates/base.html`, `main.js` |
| Custom 403, 404 and 500 pages with a link back to the feed | US12, US13 | `templates/`, `qorvli_project/views.py` |
| Django admin for moderators | US14 | `accounts/admin.py`, `posts/admin.py` |

### Screenshots

| Desktop | Mobile |
|---|---|
| ![Post with comments](docs/screenshots/post-comments-desktop.png) | ![Feed on mobile](docs/screenshots/feed-mobile.png) |
| ![Profile page](docs/screenshots/profile-desktop.png) | ![Profile on mobile](docs/screenshots/profile-mobile.png) |
| ![Search results](docs/screenshots/search-desktop.png) | ![Mobile menu](docs/screenshots/menu-mobile.png) |
| ![Delete confirmation](docs/screenshots/delete-confirm-desktop.png) | |
| ![Login page](docs/screenshots/login.png) | |

### Possible future features

- Editing comments (currently a comment can be deleted and re-posted).
- Following members and a "following only" feed filter.
- Separate clubs/groups within one installation.
- Email notifications for comments on your posts.

---

## 4. UX design

### Wireframes

Wireframes for the main screens are in [`docs/wireframes/`](docs/wireframes/):

- [`01-feed-wireframe.svg`](docs/wireframes/01-feed-wireframe.svg): navbar
  with search, a post composer, post cards with like/comment actions, and a
  "suggested users" sidebar on wide screens.
- [`02-profile-wireframe.svg`](docs/wireframes/02-profile-wireframe.svg):
  banner, avatar, bio and details, an edit button (owner only), and that
  user's posts.
- [`03-auth-wireframe.svg`](docs/wireframes/03-auth-wireframe.svg): login
  and sign-up screens, showing where validation errors appear.
- [`04-mobile-responsive-wireframe.svg`](docs/wireframes/04-mobile-responsive-wireframe.svg):
  the single-column layout with a hamburger menu below the 992px breakpoint.

### Design principles applied

- **Information hierarchy:** semantic HTML (`<nav>`, `<main>`, `<article>`,
  `<aside>`, `<footer>`) and one `<h1>` per page, with each post's author
  as its heading. The feed is newest-first; the composer sits at the top
  because posting is the primary action.
- **User control and feedback:** likes update instantly; submit buttons
  show a spinner while saving; every create, update and delete shows a
  success or error message; after editing a post or commenting, the user is
  returned to that post on the feed (`#post-<id>`).
- **Confirmation:** deleting a post or comment always asks for confirmation
  in a modal first.
- **Consistency:** cards, buttons, inputs and messages share the same
  `qorvli-*` component classes on every page.
- **No dead ends:** unknown URLs show a custom 404 page and forbidden actions
  a 403 page, both with a button back to the feed.
- **Never asking for known information:** the composer and comment forms
  never ask for a name or email; the signed-in user is used automatically.
- **Accessibility:** every input has an associated `<label>` (visually
  hidden where the design shows a placeholder), help text and errors are
  linked with `aria-describedby`, icon-only buttons have `aria-label`s,
  decorative icons are `aria-hidden`, toggle and like states are exposed
  with `aria-expanded`/`aria-pressed`, flash messages are announced through
  `aria-live`, all controls are keyboard reachable, and animation is turned
  off for users who prefer reduced motion.
- **Colour:** a dark purple theme with high-contrast light text; brand
  gradients are used for primary actions so they stand out.

### Design decisions that differ from common practice

| Decision | Reason |
|---|---|
| The "Suggested for you" sidebar is hidden below 992px. | On phones it would push the feed, the main content, far down the page. |
| Comments can't be edited, only deleted. | Comments are short; delete-and-repost keeps the data model and UI simple. Listed as a future feature. |
| Members can't edit other members' content, and site staff moderate through the Django admin rather than in the main UI. | Keeps the member interface simple and makes permission checks easy to reason about. |
| `backdrop-filter` is used for the frosted-glass panels. | It keeps text readable over content scrolling under the sticky navbar. It works in all current browsers but is not recognised by every CSS validator (see `TESTING.md`). |
| `README.md`, `TESTING.md`, `LICENSE` and `Procfile` contain capitals. | These names are conventions that GitHub and Heroku look for (Heroku requires exactly `Procfile`). All other files and folders are lower-case with no spaces. |

---

## 5. Data model

Two Django apps (`accounts` and `posts`) share one PostgreSQL database
(SQLite is used automatically for local development). The database
connection is configured in a single place: the `DATABASE_URL`
environment variable read in `qorvli_project/settings.py`.

### Entity relationship diagram

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

### Tables

**User** (`accounts.User`, extends Django's `AbstractUser`)

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | BigAutoField | primary key | |
| `username` | CharField(150) | unique, required; "edit" is reserved | Login name and profile URL |
| `password` | CharField(128) | required | Salted hash, never plain text |
| `email` | EmailField | required at signup, unique (case-insensitive, checked in the form) | Contact address |
| `first_name`, `last_name` | CharField(150) | required at signup | Display name |
| `bio` | TextField | max 280 characters, optional | Short introduction |
| `location` | CharField(100) | optional | Shown on the profile |
| `profile_picture` | ImageField | optional, max 5MB, stored in `profile_pictures/` | Avatar; a generated initials avatar is used if empty |
| `date_joined` | DateTimeField | set automatically | Shown as "Joined <month year>" |
| `is_staff`, `is_superuser`, `is_active` | BooleanField | | Admin access and account status |

**Post** (`posts.Post`)

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | BigAutoField | primary key | |
| `author` | ForeignKey → User | required, `CASCADE` | Who wrote the post |
| `content` | TextField | required, 1–2000 characters, whitespace stripped | Post text |
| `image` | ImageField | optional, valid image, max 8MB, stored in `post_images/` | Attached photo |
| `created_at` | DateTimeField | set on create, indexed (descending) | Feed order |
| `updated_at` | DateTimeField | set on every save | Last edit time |

**Comment** (`posts.Comment`)

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | BigAutoField | primary key | |
| `post` | ForeignKey → Post | required, `CASCADE` | Post being discussed |
| `author` | ForeignKey → User | required, `CASCADE` | Who wrote the comment |
| `content` | CharField(500) | required, whitespace stripped | Comment text |
| `created_at` | DateTimeField | set on create | Oldest-first ordering under a post |

**Like** (`posts.Like`)

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `id` | BigAutoField | primary key | |
| `post` | ForeignKey → Post | required, `CASCADE` | Post being liked |
| `user` | ForeignKey → User | required, `CASCADE` | Who liked it |
| `created_at` | DateTimeField | set on create | |
| | | **unique together (`post`, `user`)** | One like per member per post, enforced by the database |

### Relationships

- A `User` writes many `Post`s and many `Comment`s, and gives many `Like`s
  (one-to-many each).
- A `Post` has many `Comment`s and many `Like`s (one-to-many).
- `Like` is effectively a many-to-many link between `User` and `Post`,
  modelled as its own table so it can carry a timestamp and a uniqueness
  constraint.
- Deleting a user or a post cascades to their comments and likes, so no
  orphaned rows remain.

### CRUD operations

| Entity | Create | Read | Update | Delete |
|---|---|---|---|---|
| User / profile | Sign-up page | Profile page, feed, sidebar | Edit profile (own only) | Django admin (staff) |
| Post | Composer on the feed | Feed, search, profile | Edit post (author only) | Delete with confirmation (author only) |
| Comment | Comment box under each post | Comment panel under each post | Not supported (see design decisions) | Comment author or post author |
| Like | Heart button (AJAX) | Like count and filled heart | Not applicable | Click again to unlike |

Every action is reflected immediately: forms redirect back to the updated
page with a confirmation message, and likes update in place.

---

## 6. Security

- **Secrets:** `SECRET_KEY`, `DATABASE_URL` and `CLOUDINARY_URL` are read
  from environment variables via `django-environ` and are never committed.
  `.env` is listed in `.gitignore`; `.env.example` contains placeholders
  only. The app refuses to start without a `SECRET_KEY`.
- **DEBUG** defaults to `False` and must be explicitly enabled in a local
  `.env`. It is never `True` in production.
- **HTTPS in production:** when `DEBUG=False`, the app redirects HTTP to
  HTTPS, marks session and CSRF cookies as secure, sends an HSTS header, and
  trusts Heroku's `X-Forwarded-Proto` header.
- **Clickjacking and MIME sniffing:** `X_FRAME_OPTIONS = "DENY"` and
  `SECURE_CONTENT_TYPE_NOSNIFF` are set.
- **Login required:** every page except sign-up and login requires a
  signed-in user (`@login_required`).
- **Ownership checks in the views, not just the templates:** only a post's
  author can edit or delete it; only a comment's author or the post's author
  can delete a comment. Anyone else gets the custom 403 page, even when
  sending requests directly. These checks are covered by automated tests.
- **CSRF protection** on every form and on the AJAX like request.
  Data-changing views only accept `POST`.
- **Safe redirects:** after login, `?next=` is only followed if it points
  to this site, which prevents open-redirect phishing.
- **Logout is POST-only,** so another site can't log users out with a link.
- **Passwords** are checked by Django's validators (length, similarity,
  common and numeric-only passwords) and stored as salted hashes.
- **Uploads** must be valid images within a size limit; they are stored on
  Cloudinary in production, not on the web server.
- **Admin area:** the database can only be reached through the code and
  the Django admin, which is restricted to staff accounts.
- **Supported dependencies:** Django 5.2 LTS and patched versions of all
  other packages (see `requirements.txt`).

---

## 7. Technologies used

| Area | Technology |
|---|---|
| Languages | Python 3.11, HTML5, CSS3, JavaScript (ES6) |
| Framework | [Django 5.2 LTS](https://www.djangoproject.com/) |
| Database | PostgreSQL (Heroku Postgres) in production, SQLite locally |
| Front-end libraries | [Bootstrap 5.3](https://getbootstrap.com/), [Bootstrap Icons](https://icons.getbootstrap.com/), Google Fonts (Poppins, Inter) |
| Python packages | `django-environ` (settings from environment), `dj-database-url` (database URL parsing), `psycopg2-binary` (PostgreSQL driver), `Pillow` (image validation), `whitenoise` (static files), `gunicorn` (production server), `cloudinary` + `django-cloudinary-storage` (image hosting) |
| Hosting | Heroku |
| Tools | Git and GitHub, `flake8`, W3C Nu HTML Checker, W3C CSS Validator, JSHint, Chrome DevTools |

---

## 8. Testing

Testing is documented in full in [`TESTING.md`](TESTING.md): automated
tests, code validation, user-story testing, manual and responsive testing,
and a log of every bug found with its fix.

```bash
python manage.py test                      # automated tests
flake8 .                                   # PEP8 style (settings in setup.cfg)
python manage.py makemigrations --check    # no unapplied model changes
```

**Code style:** Python follows PEP8 with its default settings, including the
79-character line limit. Auto-generated `migrations/` are excluded.

---

## 9. Local setup

Requirements: Python 3.11 (pinned in `.python-version`), Git, and optionally
PostgreSQL (SQLite is used automatically if `DATABASE_URL` is not set).

```bash
git clone https://github.com/mdali-1991/qorvli.git
cd qorvli

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # Windows: copy .env.example .env
```

Generate a secret key and paste it into `.env` as `SECRET_KEY=...`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

For local development set `DEBUG=True` in `.env`. Either leave
`DATABASE_URL` empty/removed to use SQLite, or point it at a local Postgres
database (`createdb qorvli_db`). Then:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/signup/` to create an account, then
`http://127.0.0.1:8000/` for the feed and `http://127.0.0.1:8000/admin/` for
the Django admin.

Media (uploaded images) are saved to the local `media/` folder in
development. In production the filesystem is ephemeral, so set the
`CLOUDINARY_URL` environment variable (free Cloudinary account) and uploads
are stored there instead (see `qorvli_project/settings.py`).

### Environment variables

| Variable | Required | Example / default | Purpose |
|---|---|---|---|
| `SECRET_KEY` | Yes | long random string | Django cryptographic signing. The app refuses to start without it. |
| `DEBUG` | No | `False` (default) | Set `True` only for local development. |
| `ALLOWED_HOSTS` | In production | `your-app.herokuapp.com` | Comma-separated host names the app will serve. |
| `CSRF_TRUSTED_ORIGINS` | In production | `https://your-app.herokuapp.com` | Origins allowed to submit forms over HTTPS. |
| `DATABASE_URL` | In production | set automatically by Heroku Postgres | Database connection; falls back to SQLite locally. |
| `CLOUDINARY_URL` | In production | `cloudinary://KEY:SECRET@CLOUD_NAME` | Stores uploaded images on Cloudinary. |
| `SECURE_HSTS_SECONDS` | No | `3600` | HSTS max-age when `DEBUG=False`. |
| `SECURE_SSL_REDIRECT` | No | `True` | Redirect HTTP to HTTPS when `DEBUG=False`. |

None of these values are committed: `.env` is listed in `.gitignore`, and
`.env.example` contains placeholders only.

---

---

## 10. Deploying to Heroku

The repository root contains everything Heroku needs to detect and run the
app:

| File | Role |
|---|---|
| `requirements.txt` | Tells Heroku this is a Python app and lists the dependencies. |
| `.python-version` | Pins Python 3.11. |
| `Procfile` | `release: python manage.py migrate` runs migrations on every deploy; `web: gunicorn qorvli_project.wsgi` starts the server. |
| `STATIC_ROOT` in `settings.py` | Lets the Python buildpack run `collectstatic` automatically during the build; WhiteNoise then serves the hashed files. |

### Option A: Heroku dashboard (GitHub integration)

1. Create a free [Cloudinary](https://cloudinary.com/) account and copy the
   **API environment variable** (`cloudinary://...`) from its dashboard.
2. In the [Heroku dashboard](https://dashboard.heroku.com/), click
   **New → Create new app**, choose a name and region.
3. **Resources** tab: add the **Heroku Postgres** add-on. This sets
   `DATABASE_URL` for you.
4. **Settings → Reveal Config Vars**: add `SECRET_KEY`, `DEBUG=False`,
   `CLOUDINARY_URL`, `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`. Use the app
   domain shown under **Settings → Domains** (for example
   `your-app-1a2b3c4d5e6f.herokuapp.com`) and prefix it with `https://` for
   `CSRF_TRUSTED_ORIGINS`.
5. **Deploy** tab: choose **GitHub**, connect this repository, select the
   branch, and click **Deploy Branch** (optionally enable automatic deploys).
6. Watch the build log: dependencies install, `collectstatic` runs, and the
   `release` phase applies migrations.
7. Create an admin account: **More → Run console** →
   `python manage.py createsuperuser`.
8. Click **Open app**.

### Option B: Heroku CLI

```bash
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
heroku config:set DEBUG=False
heroku config:set CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
heroku domains     # shows the exact your-app-name-xxxx.herokuapp.com host
heroku config:set ALLOWED_HOSTS=your-app-name-xxxx.herokuapp.com
heroku config:set CSRF_TRUSTED_ORIGINS=https://your-app-name-xxxx.herokuapp.com

git push heroku main            # or: git push heroku <your-branch>:main

heroku run python manage.py createsuperuser
heroku open
```

Migrations run automatically in the `release` phase, so no manual
`migrate` step is needed.

### After deploying

- Confirm `DEBUG` is `False`: visiting a non-existent URL should show the
  custom 404 page, never a Django debug page.
- Re-run the manual tests in [`TESTING.md`](TESTING.md) against the live
  site and record the results.
- If the build fails with `ImproperlyConfigured: Set the SECRET_KEY
  environment variable`, the config var was missing when `collectstatic`
  ran; add it and redeploy.
- `DisallowedHost` or a 400 error means `ALLOWED_HOSTS` doesn't match the
  app domain; a CSRF 403 on form submission means `CSRF_TRUSTED_ORIGINS` is
  missing `https://`.

---

---

## 11. Project structure

```
.
├── .env.example          # Template for local environment variables (no real secrets)
├── .gitignore            # Keeps .env, db.sqlite3, media/, staticfiles/ out of Git
├── .python-version       # Python 3.11 for Heroku
├── Procfile              # Heroku release (migrate) + web (gunicorn) processes
├── requirements.txt      # Python dependencies (pinned)
├── setup.cfg             # flake8 / pycodestyle configuration
├── manage.py
├── qorvli_project/       # Settings, root URLs, 403/404/500 views, WSGI/ASGI
├── accounts/             # Custom User model, sign-up/login/profile views, forms, tests
├── posts/                # Post, Comment, Like models, views, forms, tests
├── templates/            # Shared base layout + 403/404/500 pages
├── static/
│   ├── css/style.css     # All custom styles
│   ├── js/main.js        # Likes (AJAX), comment panels, form spinners, fallbacks
│   └── images/           # Logos and the default avatar (SVG)
├── docs/
│   ├── wireframes/       # UX wireframes
│   └── screenshots/      # Screenshots used in this README
├── README.md
└── TESTING.md            # Testing procedure, results and bug log
```

Configuration lives in one settings file, `qorvli_project/settings.py`.
Everything that differs between development and production (debug mode,
database, hosts, image storage) is controlled by environment variables
rather than separate settings files, so the same code runs in both.

---

## 12. Development process

- **Planning:** the purpose, target audience and core loop are set out in
  [section 1](#1-purpose-and-rationale), and the user stories in
  [section 2](#2-user-stories).
- **Design:** wireframes for the feed, profile, auth and mobile layouts are
  in `docs/wireframes/`, and the data model is documented in
  [section 5](#5-data-model).
- **Build:** a custom user model (`accounts`) and the posting features
  (`posts`) as two Django apps, with the project configuration in
  `qorvli_project/`.
- **Testing:** automated tests for every view and permission rule,
  validation of HTML, CSS, JavaScript and Python, and manual testing on
  desktop and mobile. Bugs and their fixes are logged in `TESTING.md`.
- **Deployment:** Heroku with Heroku Postgres and Cloudinary, configured
  through environment variables.

The project is version-controlled with Git and hosted on GitHub; the
commit history records each change with a descriptive message.

---

## 13. Attribution and credits

- [Django](https://www.djangoproject.com/) and its documentation.
- [Bootstrap 5](https://getbootstrap.com/) and
  [Bootstrap Icons](https://icons.getbootstrap.com/), loaded from the
  jsDelivr CDN (credited in comments in `templates/base.html` and the error
  pages).
- Fonts: [Poppins and Inter](https://fonts.google.com/) via Google Fonts.
- Fallback avatars generated by [ui-avatars.com](https://ui-avatars.com/)
  (`accounts/models.py`), with a local default image if that service is
  unavailable.
- `getCookie()` in `static/js/main.js` is taken from the
  [Django CSRF documentation](https://docs.djangoproject.com/en/5.2/howto/csrf/)
  (credited in a comment above the function).
- Image hosting: [Cloudinary](https://cloudinary.com/) via
  `django-cloudinary-storage`; static files served by
  [WhiteNoise](https://whitenoise.readthedocs.io/).
- Screenshots in `docs/screenshots/` were taken from the running
  application with sample content written for this README. The laptop and
  phone mockup at the top (`hero.png`) is built from those screenshots.
- Apart from the items above, all application code (models, views, forms,
  templates, CSS and JavaScript) was written for this project; no
  walkthrough project code was copied.
