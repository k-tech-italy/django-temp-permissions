import logging
import os

import click
from strategy_field.utils import import_by_name

import django_temporary_permissions

from .. import get_full_version
from .utils import Verbosity


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('django_temporary_permissions %s' % get_full_version())
    click.echo('Using settings: %s' % os.environ.get('DJANGO_SETTINGS_MODULE'))
    ctx.exit()


_global_options = [
    click.option('-v', '--verbose',
                 default=1,
                 type=Verbosity,
                 count=True),
    click.option('-q', '--quiet',
                 default=0, is_flag=True, type=Verbosity),
    click.option('--version', is_flag=True, callback=print_version,
                 expose_value=False, is_eager=True),
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


@click.group(invoke_without_command=True)
@global_options
@click.pass_context
def cli(ctx, verbose, **kwargs):
    from django_temporary_permissions.config import env
    if verbose > 0:
        click.echo('django_temporary_permissions %s' % get_full_version())
        click.secho('Settings: %s' % os.environ['DJANGO_SETTINGS_MODULE'])

    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))

    ctx.obj = {'env': env,
               }


cli.add_command(import_by_name('django_temporary_permissions.cli.commands.upgrade.upgrade'))

logger = logging.getLogger('django_temporary_permissions.cli')
EXTENSIONS = os.environ.get('EXTENSIONS', '')


def main():  # pragma: no cover
    for extension in EXTENSIONS.split(','):
        try:
            if extension:
                commands = import_by_name(f'{extension}.cli.commands')
                for cmd in commands:
                    cli.add_command(import_by_name(cmd))

        except (ImportError, AttributeError,) as e:
            logger.warning(e)

    os.environ['LOG_LEVEL'] = 'ERROR'
    cli(prog_name=django_temporary_permissions.NAME, obj={}, max_content_width=100)
