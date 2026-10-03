/**
 * QORVLI main.js
 * Handles AJAX like toggling, comment panel expansion, and small UX polish.
 */

/*
 * getCookie() is taken from the Django documentation, "Cross Site Request
 * Forgery protection - Acquiring the token if CSRF_USE_SESSIONS and
 * CSRF_COOKIE_HTTPONLY are False":
 * https://docs.djangoproject.com/en/5.0/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
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

document.addEventListener("DOMContentLoaded", function () {
    initLikeButtons();
    initCommentToggles();
    initFileLabels();
    initAutoDismissAlerts();
    initSubmitSpinners();
    initScrollReveal();
});

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
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(function (data) {
                    const icon = button.querySelector("i");
                    const countSpan = button.querySelector(".qorvli-like-count");

                    countSpan.textContent = data.like_count;
                    button.setAttribute("aria-pressed", data.liked ? "true" : "false");
                    button.setAttribute("aria-label", data.liked ? "Unlike this post" : "Like this post");

                    if (data.liked) {
                        button.classList.add("liked");
                        icon.classList.remove("bi-heart");
                        icon.classList.add("bi-heart-fill");
                    } else {
                        button.classList.remove("liked");
                        icon.classList.remove("bi-heart-fill");
                        icon.classList.add("bi-heart");
                    }

                    button.classList.add("pop");
                    setTimeout(function () {
                        button.classList.remove("pop");
                    }, 300);
                })
                .catch(function () {
                    showToast("Something went wrong. Please try again.", "danger");
                })
                .finally(function () {
                    button.disabled = false;
                });
        });
    });
}

function initCommentToggles() {
    document.querySelectorAll(".qorvli-comment-toggle").forEach(function (button) {
        button.addEventListener("click", function () {
            const targetSelector = button.getAttribute("data-target");
            const target = document.querySelector(targetSelector);
            if (!target) return;

            const bsCollapse = bootstrap.Collapse.getOrCreateInstance(target, { toggle: false });
            bsCollapse.toggle();

            // Keep the button's aria-expanded state in sync for screen readers.
            target.addEventListener(
                "shown.bs.collapse",
                function () {
                    button.setAttribute("aria-expanded", "true");
                },
                { once: true }
            );
            target.addEventListener(
                "hidden.bs.collapse",
                function () {
                    button.setAttribute("aria-expanded", "false");
                },
                { once: true }
            );
        });
    });
}

function initFileLabels() {
    document.querySelectorAll(".qorvli-file-label input[type='file']").forEach(function (input) {
        input.addEventListener("change", function () {
            const label = input.closest(".qorvli-file-label");
            if (input.files && input.files.length > 0) {
                label.classList.add("has-file");
                const labelText = label.querySelector(".qorvli-file-label-text");
                if (labelText) {
                    labelText.textContent = input.files[0].name;
                }
            }
        });
    });
}

function initAutoDismissAlerts() {
    document.querySelectorAll(".qorvli-alert").forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });
}

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
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alertDiv);
        if (bsAlert) {
            bsAlert.close();
        }
    }, 6000);
}

function createMessagesContainer() {
    const container = document.createElement("div");
    container.className = "qorvli-messages";
    const main = document.querySelector(".qorvli-main .container");
    if (main) {
        main.insertBefore(container, main.firstChild);
    }
    return container;
}
