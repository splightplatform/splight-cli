import click
from .context import Context

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Context()
