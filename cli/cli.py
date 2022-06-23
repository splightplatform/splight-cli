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


@cli.command()
@pass_context
def configure(context: Context) -> None:
    """
    Configure Splight Hub.\n
    """
    try:
        # Precondition: Config file already exists
        # It is created when a command is run

        with open(CONFIG_FILE, 'r') as file:
            config_manager = ConfigManager(file)
            config = config_manager.load_config()

        for config_var in HUB_CONFIGS:
            old_value = config.get(config_var)
            hint = ' [' + old_value.replace(old_value[:-3], "*"*(len(old_value)-3)) + ']' if old_value is not None else ''

            if config_var in ["SPLIGHT_HUB_API_HOST", "SPLIGHT_PLATFORM_API_HOST"]:
                if old_value is not None:
                    hint = f" [{old_value}]"
                else:
                    hint = eval(config_var)
                    hint = f" [{hint}]"
                    
            value = click.prompt(click.style(f"{config_var}{hint}", fg="yellow"), type=str, default="", show_default=False)
            if value != "":
                assert len(value) > 5 , f"{config_var} is too short"
                config[config_var] = value
            else:
                if config_var in ["SPLIGHT_HUB_API_HOST", "SPLIGHT_PLATFORM_API_HOST"] and old_value is None:
                    config[config_var] = eval(config_var)

        with open(CONFIG_FILE, 'w+') as file:
            config_manager = ConfigManager(file)
            config_manager.write_config(config)
        
        click.secho(f"Configuration saved successfully", fg="green")

    except Exception as e:
        click.secho(f"Error configuring Splight Hub: {str(e)}", fg="red")
        return