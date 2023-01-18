import click
from click_default_group import DefaultGroup

from cli.context import Context, pass_context, needs_credentials
from cli.version import __version__


@click.group()
@click.version_option(version=__version__, message="%(version)s")
@click.pass_context
def cli(ctx):
    ctx.obj = Context()


@cli.group()
@pass_context
@needs_credentials
def component(ctx):
    ctx.obj = Context()


@cli.group()
@pass_context
@needs_credentials
def datalake(ctx):
    ctx.obj = Context()


@cli.group()
@pass_context
@needs_credentials
def database(ctx):
    ctx.obj = Context()


@cli.group()
@pass_context
@needs_credentials
def deployment(ctx):
    ctx.obj = Context()


@cli.group()
@pass_context
def workspace(ctx):
    ctx.obj = Context()


@cli.group(cls=DefaultGroup, default="config", default_if_no_args=True)
@pass_context
def configure(ctx: Context, from_json: str = False) -> None:
    ctx.obj = Context()
