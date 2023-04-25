import json
from typing import List, Optional

import typer
import requests
from rich.console import Console
from splight_models import Component, InputParameter, ComponentObject, Component

from cli.constants import error_style
from cli.engine.manager import ResourceManager, ResourceManagerException
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


def update_parameters(previous: List[InputParameter], hub: List[InputParameter]):
    """
    Create parameters for a new component from lists of InputParameters or Parameters.
    Assumes that equality in name, type and multiple is enough to match parameters.
    In such case the value of the previous input is used.
    """
    hub_parameters = {(x.name, x.type, x.multiple): {
        k: v for k, v in vars(x).items()} for x in hub}
    prev_parameters = {(x.name, x.type, x.multiple): {
        k: v for k, v in vars(x).items()} for x in previous}
    result = []
    # overwrite hub parameters with previous values
    for param in prev_parameters.keys():
        if param in hub_parameters.keys():
            hub_parameters[param]["value"] = prev_parameters[param]["value"]
            result.append(InputParameter(**hub_parameters[param]))
    # add new parameters
    for param in hub_parameters.keys():
        if param not in prev_parameters.keys():
            parameter = hub_parameters[param]
            if not parameter['value'] and parameter['required']:
                new_value = SpecLoader._prompt_param(parameter,
                                                     prefix="Input value for parameter")
                parameter['value'] = new_value
            result.append(InputParameter(**parameter))

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
            Component, 
            id=from_component_id, 
            first=True
        )
    except requests.exceptions.HTTPError:
        console.print(BadComponentId(from_component_id), style=error_style)

    hub_component_name, hub_component_version = from_component.version.split("-", 1)
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

    name, bindings, version = f'{from_component.name}-{version}', hub_component.bindings, f'{hub_component.name}-{version}'
    endpoints, commands, component_type = hub_component.endpoints, hub_component.commands, hub_component.component_type
    output, description = hub_component.output, hub_component.description
    custom_types, component_type = hub_component.custom_types, hub_component.component_type
    new_inputs = update_parameters(from_component.input, hub_component.input)

    component = Component(
        name=name,
        bindings=bindings,
        version=version,
        endpoints=endpoints,
        commands=commands,
        component_type=component_type,
        output=output,
        description=description,
        custom_types=custom_types,
        input=new_inputs
    )

    new_component = db_client.save(component)
    from_component_objects = [x for x in db_client.get(ComponentObject, component_id=from_component.id)]
    import ipdb
    ipdb.set_trace()
    console.print(
        f"Component {name} upgraded to version {version} of {hub_component_name}!")
    return


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
