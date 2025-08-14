import os
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse

from cryptography.fernet import Fernet
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
from environ import Env
from smart_env import SmartEnv

from django_temporary_permissions.flags import parse_bool


def parse_emails(value):
    admins = value.split(",")
    v = [(a.split("@")[0].strip(), a.strip()) for a in admins]
    return v


OPTIONS = dict(
    ADMINS=(parse_emails, ""),
    ADMIN_PANEL_URL=(str, "admin"),
    TEST_USERS=(parse_emails, ""),
    DATABASE_URL=(str, "psql://postgres:@127.0.0.1:5432/django_temporary_permissions_db"),
    DEBUG=(bool, False),
    DEV_FOOTER_INFO=(str, uuid.uuid4()),
    EMAIL_BACKEND=(str, "django.core.mail.backends.smtp.EmailBackend"),
    EMAIL_HOST=(str, "smtp.gmail.com"),
    EMAIL_HOST_USER=(str, "noreply@k-tech.it"),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_FROM_EMAIL=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_SUBJECT_PREFIX=(str, "[django_temporary_permissions]"),
    EMAIL_USE_LOCALTIME=(bool, False),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_USE_SSL=(bool, False),
    EMAIL_TIMEOUT=(int, 30),
    MEDIA_ROOT=(str, os.path.join(tempfile.gettempdir(), "django_temporary_permissions", "media")),
    STATIC_ROOT=(str, str(Path(__file__).parent.parent / "web/static")),
    ADMIN_USERNAME=(str, ""),
    ADMIN_PASSWORD=(str, ""),
    ADMIN_EMAIL=(str, ""),
    # Sentry
    SENTRY_DSN=(str, ""),
    SENTRY_SECURITY_TOKEN=(str, ""),
    SENTRY_SECURITY_TOKEN_HEADER=(str, "X-Sentry-Token"),
    SENTRY_DEBUG=(bool, False),
    SENTRY_ENVIRONMENT=(str, "local"),
    # # Django debug toolbar
    DDT_KEY=(str, get_random_string(length=12)),
    DDT_PANELS=(
        list,
        [
            "debug_toolbar.panels.timer.TimerPanel",
            "debug_toolbar.panels.settings.SettingsPanel",
            "debug_toolbar.panels.headers.HeadersPanel",
            "debug_toolbar.panels.request.RequestPanel",
            "debug_toolbar.panels.sql.SQLPanel",
            "debug_toolbar.panels.staticfiles.StaticFilesPanel",
            "debug_toolbar.panels.templates.TemplatesPanel",
            # 'debug_toolbar.panels.logging.LoggingPanel',
            "debug_toolbar.panels.redirects.RedirectsPanel",
            "debug_toolbar.panels.signals.SignalsPanel",
            "debug_toolbar.panels.profiling.ProfilingPanel",
        ],
    ),
    # Security
    SECRET_KEY=(str, "--"),
    FERNET_KEY=(str, Fernet.generate_key().decode("utf-8")),
    INTERNAL_IPS=(list, ["127.0.0.1", "localhost"]),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CSRF_COOKIE_SAMESITE=(str, "strict"),
    SESSION_COOKIE_SAMESITE=(str, "lax"),
    CSRF_TRUSTED_ORIGINS=(list, ""),
    FORCE_DEBUG_SSL=(bool, False),
    SECURE_HSTS_SECONDS=(int, 0),
    SECURE_HSTS_PRELOAD=(bool, False),
    SECURE_PROXY_SSL_HEADER=(list, []),  # Set to "HTTP_X_FORWARDED_PROTO,https" behind SSL terminator
    SECURE_SSL_REDIRECT=(bool, False),
    USE_X_FORWARDED_HOST=(bool, "false"),
    USE_HTTPS=(bool, False),
)

class SmartEnv2(SmartEnv):
    def cache_url(self, var=Env.DEFAULT_CACHE_ENV, default=Env.NOTSET, backend=None):
        v = self.str(var, default)
        if v.startswith("redisraw://"):
            scheme, string = v.split("redisraw://")
            host, *options = string.split(",")
            config = dict([v.split("=", 1) for v in options])
            if parse_bool(config.get("ssl", "false")):
                scheme = "rediss"
            else:
                scheme = "redis"
            auth = ""
            credentials = [config.pop("user", ""), config.pop("password", "")]
            if credentials[0] or credentials[1]:
                auth = f"{':'.join(credentials)}@"
            new_url = f"{scheme}://{auth}{host}/?{urlencode(config)}"
            return self.cache_url_config(urlparse(new_url), backend=backend)
        return super().cache_url(var, default, backend)


env = SmartEnv2(**OPTIONS)