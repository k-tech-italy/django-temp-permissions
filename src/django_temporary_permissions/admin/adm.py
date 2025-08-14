import logging

from django.contrib.admin.sites import site
from django_temporary_permissions import __version__

site.site_title = "django-temporary-permissions"
site.site_header = "django-temporary-permissions admin console " + __version__
site.enable_nav_sidebar = True


logger = logging.getLogger(__name__)
