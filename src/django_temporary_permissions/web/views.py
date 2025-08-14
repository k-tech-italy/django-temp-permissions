import logging

from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Home view."""

    template_name = "home.html"
