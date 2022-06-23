import click
from .context import *
from .settings import *
from .utils import *

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


@cli.group()
@click.pass_context
def storage(ctx):
    ctx.obj = Context()


@cli.group()
@click.pass_context
def workspace(ctx):
    ctx.obj = Context()


@cli.command()
@pass_context
@click.option("-j", "--from-json", help="Configuration by json instaed of prompt.")
def configure(context: Context, from_json=False) -> None:
    try:
        if from_json:
            from_json = json.loads(from_json)
        for config_var, config_var_attrs in CONFIG_VARS.items():
            default = getattr(context, config_var, None)
            # sanitize default if needed
            public_default = default
            if default and config_var_attrs.get('private', False):
                public_default = f'****{default[-3:]}'
            if not from_json:
                value = click.prompt(click.style(config_var, fg='yellow'), type=str, default=public_default, show_default=True)
            else:
                value = from_json.get(config_var, None)
            # revert sanitization if needed
            if value == public_default and config_var_attrs.get('private', False):
                value = default
            setattr(context, config_var, value)
        context.save_workspace()
        click.secho(f"Configuration saved successfully", fg="green")

    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return
