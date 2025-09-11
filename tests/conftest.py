import os
import django


def pytest_configure() -> None:
    os.environ.update(DJANGO_SETTINGS_MODULE="tests.demoapp.demo.settings")
    django.setup()
