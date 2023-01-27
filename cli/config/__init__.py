import sys
import json

import typer

from cli.settings import SplightCLISettings, CONFIG_VARS

config_app = typer.Typer(
    name="Splight CLI Configure",
    add_completion=True,
)


@config_app.callback(invoke_without_command=True)
def config(
    ctx: typer.Context,
    from_json: str = typer.Option(
        None,
        "--from-json",
        help="Configuration by json instaed of prompt")
):
    if ctx.invoked_subcommand:
        return

    cli_context = ctx.obj
    try:
        if from_json:
            from_json = json.loads(from_json)
            new_settings = SplightCLISettings.parse_obj(from_json)
        else:
            new_settings_data = {}
            for config_var in CONFIG_VARS:
                default = getattr(
                    cli_context.workspace.settings, config_var, None
                )
                value = typer.prompt(
                    typer.style(config_var, fg='yellow'),
                    type=str,
                    default=default,
                    show_default=True
                )
                new_settings_data.update({config_var: value})
            new_settings = SplightCLISettings.parse_obj(new_settings_data)
        cli_context.workspace.update_workspace(new_settings)
        typer.echo("Configuration saved successfully", color="green")
    except Exception as e:
        typer.echo(f"Error configuring Splight CLI: {str(e)}", color="red")
        sys.exit(1)


@config_app.command(name="get")
def get_variable(
    ctx: typer.Context,
    var_name: str = typer.Argument(..., help="The variable name to get value")
):
    """Prints the value of the requested variable.

    Parameters
    ----------
    ctx: Context
        The current context
    var_name:
        The variable name to get the value
    """
    variable_name = var_name.upper()
    settings = ctx.obj.workspace.settings

    if hasattr(settings, variable_name):
        value = getattr(settings, variable_name)
        typer.echo(value)


@config_app.command(name="set")
def set_variable(
    ctx: typer.Context,
    var_name: str = typer.Argument(..., help="The variable name to update"),
    value: str = typer.Argument(..., help="The new value")
):
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
    settings = ctx.obj.workspace.settings

    if hasattr(settings, variable_name):
        setattr(settings, variable_name, value)
        ctx.obj.workspace.update_workspace(settings)
