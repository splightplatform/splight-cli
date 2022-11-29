import logging

import click

from cli.cli import deployment as deployment_cli
from cli.context import Context, pass_context
from cli.deployment.deployment import DeploymentHandler
from cli.utils import Printer

logger = logging.getLogger()


@deployment_cli.command()
@pass_context
def list(context: Context) -> None:
    try:
        client = DeploymentHandler(context)
        items = client.list()
        Printer.print_dict(
            items=items, headers=["component_id", "version"]
        )

    except Exception as e:
        click.secho(f"Error listing database: {str(e)}", fg="red")
        return
