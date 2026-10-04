/* jshint esversion: 6, browser: true */
/* global bootstrap */

/**
 * QORVLI main.js
 * Handles AJAX like toggling, comment panel expansion, and small UX polish.
 */

/*
 * getCookie() is taken from the Django documentation, "Cross Site Request
 * Forgery protection - Acquiring the token if CSRF_USE_SESSIONS and
 * CSRF_COOKIE_HTTPONLY are False":
 * https://docs.djangoproject.com/en/5.2/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie("csrftoken");

/**
 * True when Bootstrap's JavaScript bundle loaded from the CDN. If the CDN is
 * unreachable, features fall back to plain DOM behaviour instead of throwing.
 */
function hasBootstrap() {
    return typeof bootstrap !== "undefined";
}

document.addEventListener("DOMContentLoaded", function () {
    initLikeButtons();
    initCommentToggles();
    initFileLabels();
    initAutoDismissAlerts();
    initSubmitSpinners();
    initScrollReveal();
    initAvatarFallbacks();
});

/**
 * When the browser restores a page from its back/forward cache, submit
 * buttons can still be disabled and showing "Saving..." from the earlier
 * submission. Put them back to normal so the form can be used again.
 */
window.addEventListener("pageshow", function (event) {
    if (!event.persisted) return;
    document.querySelectorAll("button[aria-busy='true']").forEach(function (btn) {
        if (btn.dataset.originalHtml) {
            btn.innerHTML = btn.dataset.originalHtml;
        }
        btn.disabled = false;
        btn.removeAttribute("aria-busy");
    });
});

/**
 * Users without an uploaded picture get an avatar from the external
 * ui-avatars.com service. If that service is unreachable the image would
 * show as broken, so swap in a local default avatar instead.
 */
function initAvatarFallbacks() {
    const fallback = document.body.getAttribute("data-default-avatar");
    if (!fallback) return;

    const avatars = document.querySelectorAll(
        ".qorvli-nav-avatar, .qorvli-avatar-sm, .qorvli-avatar-xs, " +
        ".qorvli-profile-avatar, .qorvli-profile-avatar-preview"
    );
    avatars.forEach(function (img) {
        function useFallback() {
            if (img.getAttribute("src") !== fallback) {
                img.setAttribute("src", fallback);
            }
        }
        img.addEventListener("error", useFallback, { once: true });
        // The image may already have failed before this script ran.
        if (img.complete && img.naturalWidth === 0) {
            useFallback();
        }
    });
}

/**
 * Gently fades + rises each card into view as the user scrolls to it,
 * giving the feed a smoother, more polished feel instead of everything
 * popping in at once. Falls back to showing everything immediately if
 * IntersectionObserver isn't available, and is skipped entirely for
 * users who prefer reduced motion.
 */
function initScrollReveal() {
    const targets = document.querySelectorAll(
        ".qorvli-post-card, .qorvli-sidebar-card, .qorvli-composer"
    );
    if (!targets.length) return;

    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!("IntersectionObserver" in window) || prefersReducedMotion) {
        targets.forEach(function (el) {
            el.classList.add("qorvli-reveal", "is-visible");
        });
        return;
    }

    const observer = new IntersectionObserver(
        function (entries, obs) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    obs.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    targets.forEach(function (el, index) {
        el.classList.add("qorvli-reveal");
        // Small stagger so cards don't all animate in at the exact same instant.
        el.style.transitionDelay = Math.min(index * 60, 300) + "ms";
        observer.observe(el);
    });
}

/**
 * Disables the submit button and shows a spinner while a form (post composer,
 * comment form, profile edit, etc.) is submitting, so the user gets immediate
 * feedback instead of wondering whether their click registered.
 */
function initSubmitSpinners() {
    document.querySelectorAll("form").forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitBtn = form.querySelector("button[type='submit']");
            if (!submitBtn || submitBtn.disabled) return;

            submitBtn.dataset.originalHtml = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.setAttribute("aria-busy", "true");
            submitBtn.innerHTML =
                '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        });
    });
}

/**
 * Like/unlike a post without reloading the page. The server returns the
 * new state as JSON; on failure the user sees an error message.
 */
function initLikeButtons() {
    document.querySelectorAll(".qorvli-like-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            const url = button.getAttribute("data-url");
            if (!url) return;

            button.disabled = true;

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(function (response) {
                    // An expired session is redirected to the login page,
                    // which returns HTML rather than JSON.
                    if (response.redirected) {
                        throw new Error("session-expired");
                    }
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(function (data) {
                    const icon = button.querySelector("i");
                    const countSpan = button.querySelector(".qorvli-like-count");

                    if (countSpan) {
                        countSpan.textContent = data.like_count;
                    }
                    button.setAttribute("aria-pressed", data.liked ? "true" : "false");
                    button.setAttribute("aria-label", data.liked ? "Unlike this post" : "Like this post");

                    button.classList.toggle("liked", data.liked);
                    if (icon) {
                        icon.classList.toggle("bi-heart-fill", data.liked);
                        icon.classList.toggle("bi-heart", !data.liked);
                    }

                    button.classList.add("pop");
                    setTimeout(function () {
                        button.classList.remove("pop");
                    }, 300);
                })
                .catch(function (error) {
                    if (error.message === "session-expired") {
                        showToast("Your session has expired. Please sign in again.", "warning");
                    } else {
                        showToast("Something went wrong. Please try again.", "danger");
                    }
                })
                .finally(function () {
                    button.disabled = false;
                });
        });
    });
}

/**
 * Show or hide a post's comment panel when its comment button is clicked.
 */
function initCommentToggles() {
    document.querySelectorAll(".qorvli-comment-toggle").forEach(function (button) {
        const targetSelector = button.getAttribute("data-target");
        const target = targetSelector ? document.querySelector(targetSelector) : null;
        if (!target) return;

        // Keep the button's aria-expanded state in sync for screen readers.
        target.addEventListener("shown.bs.collapse", function () {
            button.setAttribute("aria-expanded", "true");
        });
        target.addEventListener("hidden.bs.collapse", function () {
            button.setAttribute("aria-expanded", "false");
        });

        button.addEventListener("click", function () {
            if (!hasBootstrap()) {
                // Without Bootstrap, toggle the panel's visibility directly.
                const isOpen = target.classList.toggle("show");
                button.setAttribute("aria-expanded", isOpen ? "true" : "false");
                return;
            }
            bootstrap.Collapse.getOrCreateInstance(target, { toggle: false }).toggle();
        });
    });
}

/**
 * Replace the composer's "Photo" label with the chosen file's name.
 */
function initFileLabels() {
    document.querySelectorAll(".qorvli-file-label input[type='file']").forEach(function (input) {
        const label = input.closest(".qorvli-file-label");
        const labelText = label ? label.querySelector(".qorvli-file-label-text") : null;
        if (!labelText) return;
        const defaultText = labelText.textContent;

        input.addEventListener("change", function () {
            const hasFile = Boolean(input.files && input.files.length > 0);
            label.classList.toggle("has-file", hasFile);
            labelText.textContent = hasFile ? input.files[0].name : defaultText;
        });
    });
}

/**
 * Fade out flash messages after six seconds.
 */
function initAutoDismissAlerts() {
    document.querySelectorAll(".qorvli-alert").forEach(function (alert) {
        setTimeout(function () {
            dismissAlert(alert);
        }, 6000);
    });
}

/**
 * Close a flash message with Bootstrap's fade animation, or simply remove it
 * if Bootstrap is unavailable.
 */
function dismissAlert(alertEl) {
    if (hasBootstrap()) {
        bootstrap.Alert.getOrCreateInstance(alertEl).close();
    } else {
        alertEl.remove();
    }
}

/**
 * Show a flash-style message created from JavaScript (e.g. a failed like).
 */
function showToast(message, type) {
    const container = document.querySelector(".qorvli-messages") || createMessagesContainer();
    const alertDiv = document.createElement("div");
    alertDiv.className = "alert qorvli-alert qorvli-alert-" + (type || "info") + " alert-dismissible fade show";
    alertDiv.setAttribute("role", "alert");
    alertDiv.innerHTML =
        '<i class="bi bi-info-circle-fill" aria-hidden="true"></i> <span></span>' +
        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
    alertDiv.querySelector("span").textContent = message;
    container.appendChild(alertDiv);

    setTimeout(function () {
        dismissAlert(alertDiv);
    }, 6000);
}

/**
 * Create the flash message area if the page didn't render one.
 */
function createMessagesContainer() {
    const container = document.createElement("div");
    container.className = "qorvli-messages";
    const main = document.querySelector(".qorvli-main .container");
    if (main) {
        main.insertBefore(container, main.firstChild);
    }
    return container;
}
