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

| Tool | Scope | Result |
|---|---|---|
| `flake8` (PEP8; `setup.cfg` allows 100-character lines) | All Python files except migrations | **No issues** |
| `python manage.py makemigrations --check` | Models vs migrations | **No changes detected** |
| W3C Nu HTML Checker (`vnu.jar`, the engine behind [validator.w3.org/nu](https://validator.w3.org/nu/)) | 16 rendered pages: login, login with errors, sign-up, sign-up with errors, feed, feed page 2 with search, empty search, own profile, another profile, edit profile, edit profile with errors, edit post, edit post with errors, 403, 404, 500 | **0 errors, 0 warnings** |
| [JSHint](https://jshint.com/) 2.13 (`esversion: 11`, `browser`, `undef`, `unused`, `bootstrap` declared as a global) | `static/js/main.js` | **No warnings** |
| W3C CSS checker (the CSS mode of the Nu checker) | `static/css/style.css` | Only the two expected items below |
| [W3C CSS Validator (Jigsaw)](https://jigsaw.w3.org/css-validator/) | `static/css/style.css` | _To record: run by direct input and save a screenshot to `docs/`_ |
| Lighthouse (Chrome DevTools) | Feed and profile, desktop and mobile | _To record on the deployed site_ |

The pages were rendered with realistic data (posts with images, comments,
likes, pagination) by the Django test client, so pages behind the login were
validated as well. To repeat this on the live site, open each page, use
"View page source", and paste it into
[validator.w3.org/nu](https://validator.w3.org/nu/#textarea).

**Expected CSS validator messages:**
- `backdrop-filter`: a current property (CSS Filter Effects Level 2)
  supported by all major browsers, used deliberately for the frosted-glass
  panels; some validator versions don't recognise it yet. This is described
  in the README's design decisions.
- `var(--...)` inside `linear-gradient()` and `box-shadow`: CSS custom
  properties can't be checked statically. Jigsaw reports these as warnings,
  not errors.

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
device emulation) and keyboard-only navigation. Tests 28–34 were added
during the final review.

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
| 34 | Live site matches development | Repeat tests 1–33 on the deployed Heroku site | Same behaviour as locally | _To record after deployment_ |

---

## 5. Responsive, browser and accessibility testing

| Check | How | Result |
|---|---|---|
| Desktop layout (1280×900) | Chromium, signed in with sample data | Two-column layout; sidebar visible; no overlap |
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

---

## 8. Known issues and unfixed bugs

No known bugs remain unfixed. Limitations, all intentional and described in
the README:

- Comments can be deleted but not edited.
- The "Suggested for you" sidebar is hidden on screens narrower than 992px.
- Some CSS validators flag `backdrop-filter` and CSS custom properties, as
  explained in [section 2](#2-code-validation).
