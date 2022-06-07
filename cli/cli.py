import click
from .context import Context

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Context()


@cli.group()
@click.pass_context
def component(ctx):
    ctx.obj = Context()

@cli.group()
@click.pass_context
def datalake(ctx):
    ctx.obj = Context()