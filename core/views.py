from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Welcome page: product name only, no product capability yet."""

    template_name = "core/home.html"
