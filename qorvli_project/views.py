"""Custom error pages used when DEBUG is False."""

from django.shortcuts import render


def custom_403(request, exception=None):
    """Render the 'permission denied' page."""
    return render(request, "403.html", status=403)


def custom_404(request, exception=None):
    """Render the 'page not found' page with a link back to the feed."""
    return render(request, "404.html", status=404)


def custom_500(request):
    """Render the 'server error' page."""
    return render(request, "500.html", status=500)
