from django.shortcuts import render

# Create your views here.


def about(request):
    template = 'pages/about.html'
    # context = {'ice_cream': ice_cream_catalog[pk]}
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    # context = {'ice_cream': ice_cream_catalog[pk]}
    return render(request, template)


def page_not_found(request, exception):
    """Вернуть 404."""
    return render(request, "pages/404.html", status=404)


def csrf_failure(request, reason=""):
    """Вернуть 403."""
    return render(request, "pages/403csrf.html", status=403)


def server_error(request, exception=None):
    """Вернуть 500."""
    return render(request, "pages/500.html", status=500)
