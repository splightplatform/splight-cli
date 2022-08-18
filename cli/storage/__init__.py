import click
import logging
from cli.utils import *
from cli.cli import storage as storage_cli
from cli.context import Context, pass_context
from cli.storage.storage import Storage


logger = logging.getLogger()


@storage_cli.command()
@pass_context
def list(context: Context) -> None:
    try:
        storage = Storage(context)
        results = [r.dict() for r in storage.get()]
        Printer.print_dict(items=results, headers=["id", "file"])
    except Exception as e:
        click.secho(f"Error listing storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@click.option('--prefix', '-p', help="Prefix where to place it inside your space")
@pass_context
def load(context: Context, file: str, prefix: str = None) -> None:
    try:
        storage = Storage(context)
        storage.save(file, prefix)
        click.secho(f"Saved file: {file}", fg="green")

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error laoding storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@pass_context
def delete(context: Context, file: str) -> None:
    try:
        storage = Storage(context)
        storage.delete(file)
        click.secho(f"Deleted file: {file}", fg="green")

    except Exception as e:
        logger.exception(e)
        click.secho(f"Error deleting storage: {str(e)}", fg="red")


@storage_cli.command()
@click.argument("file", nargs=1, type=str)
@pass_context
def download(context: Context, file: str) -> None:
    try:
        storage = Storage(context)
        storage.download(file)
        click.secho(f"Donwloaded file: ./{file}", fg="green")
    except Exception as e:
        logger.exception(e)
        click.secho(f"Error deleting storage: {str(e)}", fg="red")
