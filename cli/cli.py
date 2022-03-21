import click
from .context import Context

@click.group()
@click.option('-n', "--namespace", default="default")
@click.pass_context
def cli(ctx, namespace):
    ctx.obj = Context(namespace=namespace)
