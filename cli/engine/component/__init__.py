import json
from typing import List, Optional

import typer
import requests
from rich.console import Console
from splight_models import Component, InputParameter

from cli.constants import error_style
from cli.engine.manager import ResourceManager, ResourceManagerException
from cli.utils import input_single
from .exceptions import BadComponentId, BadHubVersion, VersionUpdated
from cli.hub.component.hub_manager import HubComponentManager
from cli.component.loaders import SpecLoader


component_app = typer.Typer(
    name="Splight Engine Component",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()
MODEL = Component


@component_app.command()
def list(
    ctx: typer.Context,
    filters: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        "-f",
        help="Query param in the form key=value",
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    params = manager.get_query_params(filters)
    manager.list(params=params)


@component_app.command()
def get(
    ctx: typer.Context,
    instance_id: str = typer.Argument(..., help="The Asset's ID"),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    try:
        manager.get(instance_id)
    except ResourceManagerException as exc:
        console.print(exc, style=error_style)


@component_app.command()
def create(
    ctx: typer.Context,
    path: str = typer.Argument(
        ..., help="Path to JSON file with resource data"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    with open(path, "r") as fid:
        body = json.load(fid)
    manager.create(data=body)


def create_input(previous: List[InputParameter], hub: List[InputParameter]):
    """
    Create input for a new component from a hub component and a previous input.
    Assumes that equality in name, type and multiple is enough to match parameters.
    In such case the value of the previous input is used.
    """
    hub_inputs = {(x.name, x.type, x.multiple): {
        k: v for k, v in vars(x).items()} for x in hub}
    component_inputs = {(x.name, x.type, x.multiple): {k: v for k,
                                                       v in vars(x).items()} for x in previous}
    result = []
    # overwrite hub inputs with previous values
    for param in component_inputs.keys():
        if param in hub_inputs.keys():
            hub_inputs[param]["value"] = component_inputs[param]["value"]
            result.append(InputParameter(**hub_inputs[param]))
    # add new inputs
    for param in hub_inputs.keys():
        if param not in component_inputs.keys():
            result.append(InputParameter(**hub_inputs[param]))
    # ask for new values
    for param in result:
        if param.value is None and param.required:
            new_value = SpecLoader._prompt_param(param.__dict__,
                    prefix="Input value for parameter")
            param.value = new_value

    import ipdb
    ipdb.set_trace()
    return result


@component_app.command()
def upgrade(
        context: typer.Context,
        from_component_id: str = typer.Option(
            None, "--from", "-f",
            help="The ID of the component to be upgraded"),
        version: str = typer.Option(
            None, "--version", "-v",
            help="The version of the HubComponent to be upgraded to")
):
    """Upgrade a component to a new version of its HubComponent."""

    if not from_component_id or not version:
        console.print(
            "Component id and/or version cannot be empty", style=error_style)
    db_client = context.obj.framework.setup.DATABASE_CLIENT()
    try:
        from_component = db_client.get(
            Component, id=from_component_id, first=True
        )
    except requests.exceptions.HTTPError:
        console.print(BadComponentId(from_component_id), style=error_style)

    hub_component_name, hub_component_version = from_component.version.split(
        "-", 1)
    if hub_component_version == version:
        console.print(
            VersionUpdated(from_component.name, version),
            style=error_style
        )
        return

    manager = HubComponentManager(
        client=context.obj.framework.setup.HUB_CLIENT()
    )
    try:
        hub_component = manager.fetch_component_version(
            name=hub_component_name, version=version)
    except Exception:
        console.print(BadHubVersion(
            hub_component_name, version), style=error_style)
        return

    console.print(
        f"Upgrading component {from_component.name} {from_component.id} to version {version} of {hub_component_name}...")

    new_inputs = create_input(from_component.input, hub_component.input)
    return
    from_inputs = from_component.input
    to_inputs = hub_component.input

    for param in to_inputs:
        has_value = False

        for old in from_inputs:
            if param.name == old.name:
                param.value = old.value
                has_value = True
                break

        if not has_value:
            param.value = input_single(
                {
                    "name": param.name,
                    "type": param.type,
                    "required": param.required,
                    "multiple": param.multiple,
                    "value": param.value,
                }
            )

    # TODO: also upgrade component objects

    db_client.save(instance=to_component)


@component_app.command()
def delete(
    ctx: typer.Context,
    instance_id: str = typer.Argument(
        ..., help="The ID of the instance to be removed"
    ),
):
    manager = ResourceManager(
        client=ctx.obj.framework.setup.DATABASE_CLIENT(),
        model=MODEL,
    )
    manager.delete(instance_id)
