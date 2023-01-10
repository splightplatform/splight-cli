import sys
import json
from typing import Any

import click

from cli.cli import configure as cli_config
from cli.context import pass_context
from cli.context import Context
from cli.settings import SplightCLISettings, CONFIG_VARS


@cli_config.command()
@click.option(
    "-j",
    "--from-json",
    help="Configuration by json instaed of prompt."
)
@pass_context
def config(ctx: Context, from_json: str = False) -> None:
    try:
        if from_json:
            from_json = json.loads(from_json)
            new_settings = SplightCLISettings.parse_obj(from_json)
        else:
            new_settings_data = {}
            for config_var in CONFIG_VARS:
                default = getattr(ctx.workspace.settings, config_var, None)
                value = click.prompt(
                    click.style(config_var, fg='yellow'),
                    type=str,
                    default=default,
                    show_default=True
                )
                new_settings_data.update({config_var: value})
            new_settings = SplightCLISettings.parse_obj(new_settings_data)
        ctx.workspace.update_workspace(new_settings)
        click.secho("Configuration saved successfully", fg="green")
    except Exception as e:
        click.secho(f"Error configuring Splight CLI: {str(e)}", fg="red")
        sys.exit(1)


@cli_config.command(name="get")
@click.argument(
    "var_name"
)
@pass_context
def get_variable(ctx: Context, var_name: str) -> None:
    """Prints the value of the requested variable.

    Parameters
    ----------
    ctx: Context
        The current context
    var_name:
        The variable name to get the value
    """
    variable_name = var_name.upper()
    settings = ctx.workspace.settings

    if hasattr(settings, variable_name):
        value = getattr(settings, variable_name)
        click.secho(value)


@cli_config.command(name="set")
@click.argument(
    "var_name"
)
@click.argument(
    "value"
)
@pass_context
def set_variable(ctx: Context, var_name: str, value: Any) -> None:
    """Sets a value of a variable in the current workspace.

    Parameters
    ----------
    ctx: Context
        The current context
    var_name: str
        The variable's name to be updated
    value: Any
        The new value
    """
    variable_name = var_name.upper()
    settings = ctx.workspace.settings

    if hasattr(settings, variable_name):
        setattr(settings, variable_name, value)
        ctx.workspace.update_workspace(settings)
