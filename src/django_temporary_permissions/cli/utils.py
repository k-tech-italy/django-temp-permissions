import os
import sys
import urllib
from functools import update_wrapper

import click
from click import style

from django_temporary_permissions.exceptions import ImproperlyConfigured

_configured = False


def configure(debug=False, module=None):
    try:
        from django.conf import settings

        if module:
            os.environ["DJANGO_SETTINGS_MODULE"] = module
            os.environ["BITCASTER_SETTINGS"] = module
        if not settings._wrapped:
            settings.configure()
        import django

        django.setup()
    except Exception as e:
        if debug:
            raise
        click.secho("Error configuring environment: %s" % e, fg="red")
        sys.exit(1)


def need_setup(f):
    def new_func(*args, settings=None, **kwargs):
        if settings:
            sett = settings.type.value
        else:
            sett = None
        configure(kwargs.get("traceback", False), sett)
        return f(*args, **kwargs)

    return update_wrapper(new_func, f)


class VerbosityParamType(click.ParamType):
    name = "verbosity"

    def __init__(self) -> None:
        self.quiet = False
        self.total = 0

    def convert(self, value, param, ctx):
        self.total += value
        if param.name == "quiet":
            self.quiet = True
        if self.quiet:
            value = 0
        return int(value)


Verbosity = VerbosityParamType()

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL")


class CaseInsensitiveChoice(click.Choice):
    def convert(self, value, param, ctx):
        self.choices = [choice.upper() for choice in self.choices]
        return super().convert(value.upper(), param, ctx)


class LogLevelParamType(CaseInsensitiveChoice):
    def __init__(self, choices=LOG_LEVELS):
        super().__init__(choices)

    def convert(self, value, param, ctx):
        value = super().convert(value.upper(), param, ctx)
        os.environ["BITCASTER_LOG_LEVEL"] = value.upper()
        return value


ERROR_LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")


class ErrorLeveParamType(CaseInsensitiveChoice):
    def __init__(self, choices=ERROR_LEVELS):
        super().__init__(choices)


def wait_for_service(address, timeout=30, sleep=0.5, progress=None):
    import socket
    import time

    if isinstance(address, (list, tuple)):
        ip, port = address
    else:
        url = urllib.parse.urlparse(address)
        ip = url.hostname
        port = url.port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start = time.time()
    end = start + timeout
    attempt = 0
    while True:
        attempt += 1
        if progress:
            progress(attempt)
        try:
            s.connect((ip, port))
            s.close()
            break
        except OSError:
            time.sleep(sleep)
        except Exception as e:
            raise ImproperlyConfigured(f"Error checking {address}. {e}")
        if time.time() > end:
            raise TimeoutError
    return True


def mark(value):
    if value:
        return style("\u2714", fg="green")
    return style("\u2717", fg="red")


def yesno(value):
    return {True: "Yes", False: "No"}[value]


def echo_line(label, value, color=None):
    click.secho("%-15s: %s" % (label, value))
