import click
import logging
from cli.utils import *
from cli.cli import storage as storage_cli
from cli.context import Context, pass_context
from .storage import Storage


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


@storage_cli.command()
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Use remote resources")
@pass_context
def list(context: Context, namespace: str=None, remote: bool=False) -> None:
    try:
        storage = Storage(context, namespace)
        results = [r.dict() for r in storage.get(remote=remote)]
        Printer.print_dict(items=results, headers=["id", "file"])
    except Exception as e:
        click.secho(f"Error listing storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--prefix', '-p', help="Prefix where to place it inside your space")
@click.option('--remote', '-r', is_flag=True, help="Use remote resources")
@pass_context
def load(context: Context, file: str, namespace: str=None, prefix: str = None, remote: bool=False) -> None:
    try:
        storage = Storage(context, namespace)
        storage.save(file, prefix, remote=remote)

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error laoding storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@click.option('--namespace', '-n', help="Namespace of the resource")
@click.option('--remote', '-r', is_flag=True, help="Use remote resources")
@pass_context
def delete(context: Context, file: str, namespace: str=None, remote: bool=False) -> None:
    try:
        storage = Storage(context, namespace)
        storage.delete(file, remote=remote)

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error deleting storage: {str(e)}", fg="red")