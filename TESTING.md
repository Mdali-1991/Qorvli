# Testing: QORVLI

This document covers automated tests, code validation, user-story testing,
manual and responsive testing, and every bug found with its fix.

## Contents

1. [Automated tests](#1-automated-tests)
2. [Code validation](#2-code-validation)
3. [User-story testing](#3-user-story-testing)
4. [Manual testing](#4-manual-testing)
5. [Responsive, browser and accessibility testing](#5-responsive-browser-and-accessibility-testing)
6. [Production-configuration check](#6-production-configuration-check)
7. [Bugs found and fixed](#7-bugs-found-and-fixed)
8. [Known issues and unfixed bugs](#8-known-issues-and-unfixed-bugs)

---

## 1. Automated tests

Automated tests are in `accounts/tests.py` and `posts/tests.py`. Run them
from the repository root (a `.env` with at least `SECRET_KEY` is needed, see
`README.md`, section 9):

```bash
python manage.py test
```

**Result: 37 tests, all passing.**

| Area | What is tested |
|---|---|
| Sign-up | Page loads; valid sign-up creates the user and redirects to login; duplicate email rejected; reserved username "edit" rejected; signed-in users are redirected away |
| Login / logout | Correct and incorrect credentials; external `?next=` URLs ignored, internal ones followed; logout works by POST and rejects GET (405) |
| Profiles | Login required; another member's profile loads; edit-profile page loads and saving updates the database; fallback avatar URL generated |
| Feed and search | Login required; search filters by content; a search with no results explains why |
| Posts | Empty post rejected with a clear message; valid post created for the signed-in user; owner can edit and delete; anyone else gets the 403 page and the post is unchanged |
| Images | Valid image saved; non-image file rejected; image over 8MB rejected |
| Comments | Member can comment; blank comment rejected; comment author and post author can delete; anyone else gets 403 |
| Likes | Liking creates a like and returns JSON; liking again removes it; the database rejects a duplicate like |

---

## 2. Code validation

### Summary

| Language | Tool | Scope | Result |
|---|---|---|---|
| HTML | W3C Nu HTML Checker | 16 rendered pages | **0 errors, 0 warnings, 0 info messages** |
| CSS | W3C CSS checker (CSS mode of the Nu checker) | `static/css/style.css` | **0 errors, 0 warnings** |
| JavaScript | JSHint 2.13 | `static/js/main.js` | **0 warnings** (default and strict settings) |
| Python | `pycodestyle` and `flake8` with default PEP8 settings | All `.py` files except auto-generated migrations | **0 issues** |

The online validators at validator.w3.org and jigsaw.w3.org were blocked by
the network policy of the environment used for this audit. The HTML and CSS
were therefore checked with `vnu.jar`, the official W3C Nu checker that
runs [validator.w3.org/nu](https://validator.w3.org/nu/), installed locally.
The live-site checks below are still to be recorded.

### HTML (W3C Nu HTML Checker)

The Django test client rendered every page with realistic data (posts
with images, comments, likes, pagination) as a signed-in member, so pages
behind the login were validated too:

| Page | Result | Page | Result |
|---|---|---|---|
| Login | Pass | Own profile | Pass |
| Login with errors | Pass | Another member's profile | Pass |
| Sign-up | Pass | Edit profile | Pass |
| Sign-up with errors | Pass | Edit profile with errors | Pass |
| Feed | Pass | Edit post | Pass |
| Feed page 2 with a search | Pass | Edit post with errors | Pass |
| Search with no results | Pass | 403, 404, 500 | Pass |

A separate check confirmed every element is closed and correctly nested,
and every `<img>` has descriptive `alt` text.

**Fixed during validation:**
- Form inputs pointed `aria-describedby` at help-text and error elements
  that weren't rendered (W3C errors on sign-up and the edit pages). Each
  field now renders them with the matching ids.
- Posts on the profile page had no heading ("article lacks heading").
- Six avatars had empty `alt=""`; all now describe whose picture it is.
- The navigation wasn't inside a `<header>` landmark.
- The error pages linked home with a hard-coded `/` rather than
  `{% url 'posts:feed' %}`.

**To check on the live site:** open each page, choose "View page source",
and paste it into [validator.w3.org/nu](https://validator.w3.org/nu/#textarea)
(direct input). Logged-in pages can't be checked by URL. _Record results
and screenshots here._

### CSS (W3C CSS checker)

**Result:** 0 errors and 0 warnings for `static/css/style.css`.

**Fixed during validation (10 errors before):**
- 6 errors from CSS custom properties (`var(--…)`) inside
  `linear-gradient()` and a multi-part `box-shadow`, which validators
  can't check. These now use the literal colour values.
- 4 errors for `backdrop-filter`, which validators don't recognise. It
  was removed: on cards and messages it only blurred the plain page
  gradient, and the sticky navbar is now 94% opaque instead.

**Also cleaned up:** the stylesheet was reorganised into commented
sections with one declaration per line. Rules split across the file were
merged, and an unused class, an unused variable and redundant selectors
were removed. Before/after screenshots of 9 pages at 390, 768 and 1280px
showed no visible change.

**To check:** paste the file into the
[W3C CSS Validator (Jigsaw)](https://jigsaw.w3.org/css-validator/#validate_by_input)
and save a screenshot. _Record the result here._

### JavaScript (JSHint)

| Setting | Result |
|---|---|
| Default settings, as when pasting into [jshint.com](https://jshint.com/) (the file declares `esversion: 6` and the `bootstrap` global inline) | 0 warnings |
| Strict: `undef` and `unused` enabled | 0 warnings |
| `node --check` (syntax) | Pass |

There are no `console.log` statements. Every `fetch` has error handling
that shows the user a message.

**Fixed during the audit:**
- A missing icon or count element could have turned a successful like
  into a "Something went wrong" message. The lookups are now guarded.
- When a session expired, liking showed a generic error. It now says
  "Your session has expired. Please sign in again."
- Pages restored with the browser's Back button could leave submit
  buttons disabled showing "Saving...". They're now reset.
- Comment toggles registered new listeners on every click, and file
  labels didn't reset when a chosen file was cleared. Both are fixed.

### Python (PEP8)

| Check | Result |
|---|---|
| `pycodestyle --config=/dev/null` (pure PEP8 defaults, as used by the [CI Python Linter](https://pep8ci.herokuapp.com/)) | 0 issues |
| `flake8` (PEP8 plus unused imports and variables) | 0 issues |
| `python manage.py makemigrations --check` | No changes detected |

**Fixed during validation:** 98 lines were longer than the PEP8 limit of
79 characters, so the project had relied on a 100-character exception.
The code was reformatted with `black` at 79 columns, and long docstrings
and strings were wrapped by hand. The exception was then removed from
`setup.cfg`. Auto-generated migrations are excluded.

### Lighthouse

_To record on the deployed site:_ performance, accessibility, best
practices and SEO for the feed and a profile, on desktop and mobile.

---

## 3. User-story testing

| Story | How it was tested | Result |
|---|---|---|
| US01 Create an account | Sign-up tests; manual tests 1–2 | Pass |
| US02 Log in and out securely | Login/logout tests incl. `?next=` and POST-only logout; manual tests 3–5 | Pass |
| US03 Edit my profile | Edit-profile tests; manual test 20 | Pass |
| US04 View other members | Profile tests; manual test 21 | Pass |
| US05 Publish a post with optional photo | Post and image tests; manual tests 6–9 | Pass |
| US06 Edit my post | `test_owner_can_edit_own_post`; manual test 10 | Pass |
| US07 Delete my post after confirming | `test_owner_can_delete_own_post`; manual test 11 (confirmation modal) | Pass |
| US08 Comment on posts | Comment tests; manual test 13 | Pass |
| US09 Moderate comments on my posts | Comment-deletion tests; manual tests 14–16 | Pass |
| US10 Like without reloading | Like tests; manual test 17; browser check that the count and `aria-pressed` update | Pass |
| US11 Search posts and members | Search tests; manual tests 18–19 | Pass |
| US12 Clear feedback | Message assertions in tests; manual tests 6–20; spinners on submit | Pass |
| US13 Nobody else can change my content | 403 tests for edit/delete of posts and comments; manual tests 12 and 16 | Pass |
| US14 Admin area for moderation | Manual: staff account can manage users, posts, comments and likes at `/admin/`; non-staff can't log in there | _To record_ |

---

## 4. Manual testing

Tests 1–27 were carried out on desktop Chrome, mobile Chrome (DevTools
device emulation) and keyboard-only navigation. Tests 28–37 were added
during the final reviews.

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
| 13 | Add comment | Open comments on a post, type a comment, submit | Page returns to that post (`#post-<id>`) with the new comment and a success message | Pass |
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
| 28 | Reserved username | Sign up with the username "edit" | Form shows "This username is reserved. Please choose another." | Pass |
| 29 | Empty search | Search for a word that appears in no post or name | "No posts match ..." with a link back to all posts | Pass |
| 30 | Return to post | Comment on or edit a post further down the feed | Page reopens at that post with a success message | Pass |
| 31 | Avatar service unavailable | Block `ui-avatars.com` in DevTools (Network → Block request domain) and reload | Default avatar shown everywhere; no broken images | Pass |
| 32 | Bootstrap CDN unavailable | Block `cdn.jsdelivr.net` and reload | Page still usable; comment panels open; no JavaScript errors in the console | Pass |
| 33 | Password rules shown | Open the sign-up page | Password requirements are listed under the password field before submitting | Pass |
| 34 | Live site matches development | Repeat tests 1–37 on the deployed Heroku site | Same behaviour as locally | _To record after deployment_ |
| 35 | Back button after submitting | Submit a comment, then press Back | Buttons on the restored page work normally (not stuck on "Saving...") | Pass (restore simulated in Chromium; _confirm on the live site in Safari/Firefox_) |
| 36 | Expired session | Sign out in another tab, then like a post | "Your session has expired. Please sign in again." | Pass |
| 37 | Clear a chosen photo | Choose a photo in the composer, then cancel the selection | Label returns to "Photo" | Pass |

---

## 5. Responsive, browser and accessibility testing

| Check | How | Result |
|---|---|---|
| Desktop layout (1280×900) | Chromium, signed in with sample data | Two-column layout; sidebar visible; no overlap |
| Tablet layout (768×1024) | Chromium tablet emulation | Single column; hamburger menu; sidebar hidden; profile avatar overlaps the banner correctly; no horizontal scrolling |
| Spacing | Measured the gaps between the composer and posts at 390, 768 and 1280px | An even 24px everywhere |
| Mobile layout (390×844, iPhone 12-class) | Chromium mobile emulation | Single column; hamburger menu visible and working; **no horizontal scrolling** on feed or profile |
| Keyboard | Tab from the post box | Focus moves to the photo input, which has a visible focus ring |
| Back/forward navigation | Feed → profile → edit profile, then back twice and forward once | Pages reload correctly; no console errors |
| Reduced motion | `prefers-reduced-motion: reduce` | Scroll-in animations are skipped |
| Screen-reader names | Inspected rendered HTML | Every input has a label; icon-only buttons have `aria-label`; like and comment toggles expose `aria-pressed`/`aria-expanded` |
| Firefox, Safari, Edge | _To record_ | _To record_ |

Screenshots from these checks are in [`docs/screenshots/`](docs/screenshots/).

---

## 6. Production-configuration check

Before deploying, the app was run locally with production settings
(`DEBUG=False`, `CLOUDINARY_URL` set) to mirror Heroku:

| Check | Command | Result |
|---|---|---|
| Django deployment checklist | `python manage.py check --deploy` | No issues (HSTS preload is deliberately off for a `herokuapp.com` domain; that check is silenced in `settings.py`) |
| Static files build | `python manage.py collectstatic --noinput` | Hashed, compressed manifest generated |
| Image storage | Inspect the configured default storage | `MediaCloudinaryStorage` |
| Migrations | `python manage.py migrate` | All migrations applied |
| Production server | `gunicorn qorvli_project.wsgi` | Login page 200, CSS served by WhiteNoise, unknown URL returns the custom 404 |

---

## 7. Bugs found and fixed

| Bug | Found during | Fix |
|---|---|---|
| Comment "aria-expanded" state on the comment-toggle button never updated when using the Bootstrap collapse, so screen readers always announced it as collapsed. | Test 25 | Added `shown.bs.collapse` / `hidden.bs.collapse` listeners in `main.js` that flip `aria-expanded` on the toggle button. |
| Icon-only buttons (like, comment toggle, delete comment, "..." menu) had no accessible name. | Test 25 | Added explicit `aria-label` attributes and `aria-hidden="true"` on the decorative icons across `feed.html`, `profile.html` and `base.html`. |
| Forms gave no visual feedback between click and page response, so a slow connection made it look like nothing happened. | Test 6, 20 | Added a shared `initSubmitSpinners()` handler in `main.js` that disables the submit button and shows a spinner label while any form is submitting. |
| Missing database migrations meant the project could not be migrated on a clean checkout. | Test 1 (initial setup) | Generated and committed `accounts/migrations/0001_initial.py` and `posts/migrations/0001_initial.py`. |
| The like button's filled/unfilled state used an invalid template expression (`{% if post.is_liked_by:request.user %}`), which Django cannot resolve — so a post you had already liked still rendered with an empty heart after a page reload, even though the `Like` row existed in the database. | Test 17, re-checked after a page refresh | Annotated the `Post` queryset in `feed_view` and `profile_view` with `is_liked = Exists(Like.objects.filter(post=OuterRef("pk"), user=request.user))` and updated the templates to use `post.is_liked`, so the correct state is calculated in the database query instead of an unsupported template lookup. |
| Uploading any image crashed with a 500 error when `CLOUDINARY_URL` was not set (local development): `STORAGES` defined no `default` storage. | New automated image-upload tests | Added the filesystem storage as the default; Cloudinary replaces it in production. |
| A user who registered the username "edit" could never open their own profile, because `/accounts/profile/edit/` is the edit page. | Code review | "edit" is now a reserved username (case-insensitive) at sign-up. |
| Signed-in users could still open the sign-up page. | Code review | They are redirected to the feed. |
| An empty post showed "This field is required." instead of the custom message, because Django's required check runs before `clean_content`. | Automated test | Custom `required` error messages on the post and comment forms. |
| Error flash messages included raw field names (e.g. "content: ..."), and comment errors hid the real reason. | Manual test 7 | Messages now list the validation errors in plain language. |
| After commenting or editing, the user was sent to the top of the feed rather than back to the post. | Manual test 13 | Redirects go to `#post-<id>`. |
| "1 posts" / "1 comments" on the profile page. | Manual test 21 | Counts use Django's `pluralize` filter. |
| Forms rendered `aria-describedby` pointing at help-text/error elements that didn't exist (W3C errors on sign-up and edit pages). | W3C validation | Each field renders its help text and errors with the matching ids; sign-up now shows the password rules up front. |
| The profile banner covered the user's name and half the avatar. | Responsive testing (screenshots) | Only the avatar overlaps the banner, above it; the name sits below. |
| The mobile menu icon and the close (×) buttons on modals and messages were dark on the dark background. | Responsive testing (screenshots) | Navbar uses Bootstrap's dark theme; close buttons are light. |
| A search with no results said "No posts to show yet. Be the first to share something!" | Manual test 18 | It now says no posts match the search and links back to all posts. |
| If ui-avatars.com was unreachable, avatars showed as broken images. | Browser test with the service blocked | A local default avatar replaces any avatar that fails to load. |
| If the Bootstrap CDN failed to load, `main.js` threw "bootstrap is not defined" and comment panels stopped working. | Browser test with the CDN blocked | `main.js` checks for Bootstrap and falls back to plain DOM behaviour. |
| Below the first screen, text could appear on a white background where the page gradient didn't paint. | Full-page screenshot | Added a solid dark background colour under the gradient. |
| Django 5.0 (end of life April 2025) and gunicorn 22 (HTTP request smuggling, CVE-2024-6827) were pinned. | Dependency review | Upgraded to Django 5.2 LTS, gunicorn 23 and patched versions of the other packages. |

| 98 Python lines exceeded PEP8's 79-character limit; the project relied on a 100-character exception. | Code-quality audit | Reformatted to 79 columns; exception removed from `setup.cfg`. |
| 10 CSS validator errors (`var()` in gradients and shadows, `backdrop-filter`). | CSS validation | Literal colours in gradients and shadows; `backdrop-filter` removed. |
| Posts in the feed were 44px apart but the first post was 24px below the composer. | Responsive testing | The feed's gap alone spaces the posts: 24px everywhere. |
| The post hover lift never appeared: a later rule with equal specificity reset the transform. | CSS audit | Hover rule moved after it; still off for reduced motion. |
| Submit buttons stayed disabled ("Saving...") on pages restored with the Back button. | JavaScript audit | Reset on `pageshow` from the back/forward cache. |
| An expired session made liking show a generic error. | JavaScript audit | Specific "session has expired" message. |
| Six avatars had empty `alt` text; no `<header>` landmark; error pages linked to a hard-coded `/`. | HTML audit | Descriptive alt text, `<header>` around the navbar, `{% url %}` links. |

---

## 8. Known issues and unfixed bugs

No known bugs remain unfixed. Limitations, all intentional and described in
the README:

- Comments can be deleted but not edited.
- The "Suggested for you" sidebar is hidden on screens narrower than 992px.
