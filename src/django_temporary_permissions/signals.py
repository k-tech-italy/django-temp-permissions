from django.dispatch import Signal

django_temporary_permissions_version_upgraded = Signal(providing_args=['version'])
cli_django_temporary_permissions_upgrade_templates = Signal(providing_args=['verbosity', 'context'])
cli_django_temporary_permissions_execute_command = Signal(providing_args=['context' ])
