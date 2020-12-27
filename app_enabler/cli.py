import os
import sys
from pathlib import Path
from subprocess import CalledProcessError
from typing import List

import click

from .enable import apply_configuration_set, enable_application as enable_fun
from .errors import messages
from .install import get_application_from_package, install as install_fun


@click.group()
@click.option("--verbose", is_flag=True)
@click.pass_context
def cli(context, verbose):
    """Click entrypoint."""
    # this is needed when calling as CLI utility to put the current directory
    # in the python path as it's not done automatically
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
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
@click.argument("config_set", nargs=-1)
@click.pass_context
def apply(context: click.core.Context, config_set: List[str]):
    """
    Apply configuration stored in one or more json files.

    CONFIG_SET: Path to configuration files
    \f

    :param click.core.Context context: Click context
    :param list config_set: list of paths to addon configuration to load and apply
    """
    apply_configuration_set([Path(config) for config in config_set], verbose=context.obj["verbose"])


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
