import sys
from subprocess import CalledProcessError

import click

from .enable import enable as enable_fun
from .errors import messages
from .install import get_application_from_package, install as install_fun


@click.group()
@click.option("--verbose", is_flag=True)
@click.pass_context
def cli(context, verbose):
    """Click entrypoint."""
    context.ensure_object(dict)
    context.obj["verbose"] = verbose


@cli.command()
@click.argument("application")
@click.pass_context
def enable(context: click.core.Context, application: str):
    """
    Enable the application in the current django project.

    APPLICATION: Application module name (example: 'djangocms_blog')
    \f

    :param click.core.Context context: Click context
    :param str application: python module name to enable. It must be the name of a Django application.
    """
    enable_fun(application, verbose=context.obj["verbose"])


@cli.command()
@click.argument("package")
@click.option("--pip-options", default="", help="Additional options passed as is to pip")
@click.pass_context
def install(context: click.core.Context, package: str, pip_options: str):
    """
    Install the package in the current virtualenv and enable the corresponding application in the current project.

    \b
    PACKAGE: Package name as available on PyPi, or rather its requirement string.
             Accepts any PEP-508 compliant requirement.
             Example: "djangocms-blog~=1.2.0"
    \f

    :param click.core.Context context: Click context
    :param str package: Name of the package to install
    :param str pip_options: Additional options passed to pip
    """
    verbose = context.obj["verbose"]
    try:
        install_fun(package, verbose=verbose, pip_options=pip_options)
    except CalledProcessError:
        msg = messages["install_error"].format(package=package)
        if verbose:
            raise RuntimeError(msg)
        else:
            sys.stderr.write(msg)
            return
    application = get_application_from_package(package)
    if application:
        enable_fun(application, verbose=verbose)
    else:
        msg = messages["enable_error"].format(package=package)
        if verbose:
            raise RuntimeError(msg)
        else:
            sys.stderr.write(msg)
            return
