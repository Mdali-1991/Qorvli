"""Project middleware."""

from django.http import HttpResponseNotAllowed
from django.shortcuts import render


class MethodNotAllowedPageMiddleware:
    """Show the custom 405 page instead of Django's empty response.

    Django has no handler405 setting like handler404, so views decorated
    with @require_POST / @require_http_methods return a blank page when
    visited the wrong way (e.g. an old bookmark to /accounts/logout/).
    This replaces that response with templates/405.html, keeping the
    status code and the Allow header. AJAX requests are left unchanged.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        if isinstance(response, HttpResponseNotAllowed) and not is_ajax:
            page = render(request, "405.html", status=405)
            page["Allow"] = response["Allow"]
            return page
        return response
