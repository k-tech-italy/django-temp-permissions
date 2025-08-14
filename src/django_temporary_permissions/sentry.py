from sentry_sdk import (
    capture_exception as _capture_exception,  # noqa
    )


def capture_exception(error=None):  # noqa
    return _capture_exception(error)


def crashlog_process_exception(exception, request=None, message_user=False):  # noqa
    return _capture_exception(exception)
