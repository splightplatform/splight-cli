import click
from functools import update_wrapper
from .context import pass_context


def needs_credentials(f):
    @pass_context
    def run(ctx, *args, **kwargs):
        if ctx.SPLIGHT_ACCESS_ID is None or ctx.SPLIGHT_SECRET_KEY is None:
            click.secho(f"Please set your Splight credentials. Use \"splightcli configure\"", fg='red')
            exit(1)
        return f(ctx, *args, **kwargs)
    return update_wrapper(run, f)
