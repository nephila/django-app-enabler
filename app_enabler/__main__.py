import click

from .main import enable


@click.command()
@click.argument("application")
def cli(application):
    """
    Enable the given application in the current django project.

    :param application: python module name to enable. It must be the name of a Django application.
    :type application: str
    """
    enable(application)


if __name__ == "__main__":
    cli()
