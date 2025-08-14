from pathlib import Path

import click
from django.conf import settings

from django_temporary_permissions.cli import global_options
from django_temporary_permissions.config import env
from django_temporary_permissions.signals import (
    cli_django_temporary_permissions_execute_command,
    cli_django_temporary_permissions_upgrade_templates,
    django_temporary_permissions_version_upgraded,
)


def configure_master_app():

    pass


def configure_django_temporary_permissions_app():

    pass


def configure_beat():
    from django_celery_beat.models import CrontabSchedule, IntervalSchedule

    hourly, __ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.HOURS,
    )

    midnight, __ = CrontabSchedule.objects.get_or_create(
        minute=0,
        hour=0,
        timezone=settings.TIME_ZONE,
    )

    minute, __ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.MINUTES,
    )

    # Create Periodic tasks here


def configure_dirs(prompt, verbose):
    from django_temporary_permissions.config import env
    for _dir in ('MEDIA_ROOT', 'STATIC_ROOT'):
        target = Path(env.str(_dir))
        if not target.exists():
            if prompt:
                ok = click.prompt(f"{_dir} set to '{target}' but it does not exists. Create it now?")
            else:
                ok = True
            if ok:
                if verbose > 0:
                    click.echo(f"Create {_dir} '{target}'")
                target.mkdir(parents=True)


@click.command()  # noqa: C901
@global_options
@click.option('--prompt/--no-input', default=True, is_flag=True,
              help='Do not prompt for parameters')
@click.option('--migrate/--no-migrate', default=True, is_flag=True,
              help='Run database migrations')
@click.option('--emails/--no-emails', default=True, is_flag=True,
              help='Load email templates')
@click.option('--documents/--no-documents', default=True, is_flag=True,
              help='Load documents templates')
@click.option('--static/--no-static', default=False, is_flag=True,
              help='Collect static assets')
@click.option('--reindex/--no-reindex', default=False, is_flag=True,
              help='Run Database full reindex')
@click.option('--check/--no-check', 'run_check', default=True, is_flag=True,
              help='Run check framework')
@click.option('--traceback', '-tb', default=False, is_flag=True,
              help='Raise on exceptions')
@click.option('--admin-email', '-ae', default=env.str('ADMIN_EMAIL'), help='Do not prompt for parameters')
@click.option('--admin-username', '-au', default=env.str('ADMIN_USERNAME'), help='Do not prompt for parameters')
@click.option('--admin-password', '-ap', default=env.str('ADMIN_PASSWORD'), help='Do not prompt for parameters')
@click.pass_context
def upgrade(ctx, prompt, migrate, static, verbose, run_check,  # noqa: C901
            emails, traceback, documents, admin_username, admin_email, admin_password, **kwargs):
    """Perform any pending database migrations and upgrades."""
    import django
    from django.core.management import call_command
    from django.db.transaction import atomic

    from django_temporary_permissions.sentry import capture_exception
    from django_temporary_permissions.system import state
    state.upgrade = True
    try:

        extra = {'no_input': prompt,
                 'verbosity': verbose - 1}

        configure_dirs(prompt, verbose)
        django.setup()

        from django_temporary_permissions import get_full_version
        from django_temporary_permissions.models import SysLogEntry
        from django_temporary_permissions.system import core

        with atomic():

            if static:
                if verbose == 1:
                    click.echo('Run collectstatic')
                call_command('collectstatic', **extra)

            if migrate:
                if verbose >= 1:
                    click.echo('Run migrations')
                call_command('migrate', **extra)

                configure_django_temporary_permissions_app()
                configure_master_app()

            if documents:
                if verbose >= 1:
                    click.echo('Populate default documents')
                from django_temporary_permissions.web.views.terms import Document
                Document.objects.populate()

            if emails:
                from django_temporary_permissions.models import SystemEmailTemplate
                SystemEmailTemplate.objects.populate()

                if verbose == 1:
                    click.echo('Populate default Email Templates')
                    click.echo('Populate default Content Pages')

            cli_django_temporary_permissions_upgrade_templates.send(sender=core, verbosity=verbose, context=ctx)

            if run_check:
                from .check import check
                ctx.invoke(check, verbose=verbose, **kwargs)

            if verbose >= 1:
                click.echo('Configure default Celery Beat period tasks')
            configure_beat()

            if admin_email:
                try:
                    email = admin_email.strip()
                    validate_email(email)
                except ValidationError as e:
                    ctx.fail('\n'.join(e.messages))

                admin_password = admin_password.strip()
                if not admin_password:
                    ctx.fail('You must provide a password')
                try:
                    user = User.objects.create_superuser(admin_username, admin_email, admin_password)
                    if verbosity > 0:
                        click.echo(f'Created superuser {user.username}')
                except IntegrityError as e:
                    click.secho(f'Unable to create superuser: {e}', fg='yellow')

        cli_django_temporary_permissions_execute_command.send(sender=upgrade, context=ctx)

        last_record = SysLogEntry.objects.filter(organization__is_core=True,
                                                 extra__updated=True).first()
        current_version = get_full_version()
        if not last_record or last_record.extra.get('version', '') != current_version:
            django_temporary_permissions_version_upgraded.send(sender=core, version=current_version)
            core.logger.info('django_temporary_permissions has been updated to %s' % current_version,
                             extra={'version': current_version,
                                    'updated': True,
                                    })
    except Exception as e:
        if traceback:
            raise
        capture_exception(e)
        click.echo(str(e))
        ctx.abort()
