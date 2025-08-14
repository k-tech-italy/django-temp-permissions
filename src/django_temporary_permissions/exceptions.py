class django_temporary_permissions_Error(Exception):
    default_message = 'Error'

    def __init__(self, message=None, **kwargs):
        self.message = str(message) or self.default_message
        self.extra = kwargs


class ImproperlyConfigured(django_temporary_permissions_Error):
    pass
