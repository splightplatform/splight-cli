import click
from cli.context import *
from cli.constants import *
from cli.settings import *
from cli.utils import *

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
def database(ctx):
    ctx.obj = Context()


@cli.group()
@click.pass_context
def storage(ctx):
    ctx.obj = Context()


@cli.group()
@click.pass_context
def history(ctx):
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
            new_settings = SplightCLISettings.parse_file(from_json)
        else:
            new_settings_data = {}
            for config_var in CONFIG_VARS:
                default = getattr(context.workspace.settings, config_var, None)
                value = click.prompt(
                    click.style(config_var, fg='yellow'),
                    type=str,
                    default=default,
                    show_default=True
                )
                new_settings_data.update({config_var: value})
            new_settings = SplightCLISettings.parse_obj(new_settings_data)
        context.workspace.update_workspace(new_settings)
        click.secho(f"Configuration saved successfully", fg="green")

    except Exception as e:
        click.secho(f"Error configuring Splight CLI: {str(e)}", fg="red")
        return
