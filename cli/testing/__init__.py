import datetime
import os
from typing import Dict, List

import pytest
from cli.component.loaders import ComponentLoader, SpecLoader
from splight_lib.client.database.local_client import LocalDatabaseClient
from splight_models import (
    Asset,
    Attribute,
    Component,
    File,
    Query,
    QuerySourceType,
)

FAKE_NATIVE_TYPES = {
    "int": 1,
    "bool": True,
    "str": "fake",
    "float": 5.5,
    "datetime": datetime.datetime(2022, 12, 18),
    "url": "www.google.com",
}

FAKE_DATABASE_TYPES = {
    "Component": Component(name="ComponentTest", version="1.0.0"),
    "Asset": Asset(name="AssetTest"),
    "Attribute": Attribute(name="AttrTest"),
    "File": File(file=""),
    "Query": Query(
        name="QueryTest",
        source_type=QuerySourceType.NATIVE,
        output_format="",
        target="value",
    ),
}


def get_tests_initial_setup() -> dict:
    # TODO: this will be change when we refactor setup.configure to
    # don't override envvars
    return {
        "DATABASE_CLIENT": (
            "splight_lib.client.database.local_client.LocalDatabaseClient"
        ),
        "DATALAKE_CLIENT": (
            "splight_lib.client.datalake.local_client.LocalDatalakeClient"
        ),
        "COMMUNICATION_CLIENT": (
            "splight_lib.client.communication.local_client."
            "LocalCommunicationClient"
        ),
        "NAMESPACE": "test",
    }


def get_custom_type_fields(param, custom_types):
    for ct in custom_types:
        if ct["name"] == param["type"]:
            return ct["fields"]


def load_input_parameters(inputs_list, custom_types, db):
    for param in inputs_list:
        value = param.get("value")
        if value is None:
            type_ = param.get("type")
            multiple = param.get("multiple")
            if type_ in FAKE_NATIVE_TYPES.keys():
                value = FAKE_NATIVE_TYPES.get(type_)
            elif type_ in FAKE_DATABASE_TYPES.keys():
                instance = FAKE_DATABASE_TYPES.get(type_)
                if not instance.id:  # save to db and update fake map
                    instance = db.save(instance)
                    FAKE_DATABASE_TYPES.update({type_: instance})
                value = instance.dict()
            else:  # its a custom type
                fields = get_custom_type_fields(param, custom_types)
                value = load_input_parameters(fields, custom_types, db)
                if multiple:
                    value = [value]
        param.update({"value": value})
    flat_inputs = {param["name"]: param["value"] for param in inputs_list}
    return flat_inputs


def get_input_parameters(raw_spec: Dict) -> List[Dict]:
    db = LocalDatabaseClient(
        namespace=get_tests_initial_setup().get("NAMESPACE"),
        path=os.environ["COMPONENT_PATH_FOR_TESTING"],
    )
    inputs = raw_spec["input"]
    custom_types = raw_spec["custom_types"]
    parsed_inputs = load_input_parameters(inputs, custom_types, db)
    return parsed_inputs


@pytest.fixture
def component(mocker):
    # TODO: search a better and cleaner solution
    component_path = os.environ["COMPONENT_PATH_FOR_TESTING"]
    clients_config = {"path": component_path}

    # local database, datalake and communication clients
    initial_setup = get_tests_initial_setup()

    component_loader = ComponentLoader(path=component_path)
    spec_loader = SpecLoader(path=component_path)
    component_class = component_loader.load()
    run_spec = spec_loader.load(input_parameters={}, prompt_input=False)

    # TODO: remove, just temporal until define LocalCommunicationClient
    # #########################################################################
    mocker.patch("remote_splight_lib.communication.client.CommunicationClient")
    initial_setup[
        "COMMUNICATION_CLIENT"
    ] = "splight_lib.client.datalake.LocalDatalakeClient"
    # #########################################################################

    mocker.patch(
        "splight_lib.component.abstract.AbstractComponent."
        "_load_instance_kwargs_for_clients"
    )
    mocker.patch(
        (
            "splight_lib.component.abstract.AbstractComponent."
            "communication_client_kwargs"
        ),
        clients_config,
    )
    input_parameters = get_input_parameters(spec_loader.raw_spec)
    mocker.patch(
        "splight_lib.component.abstract.AbstractComponent.parse_parameters",
        return_value=input_parameters,
    )
    mocker.patch(
        "splight_lib.client.datalake.LocalDatalakeClient.create_index"
    )
    mocker.patch(
        "splight_lib.component.abstract.BindingsMixin._load_client_bindings"
    )
    mocker.patch("splight_lib.component.abstract.ExecutionClient")

    component = component_class(
        run_spec=run_spec.dict(),
        initial_setup=initial_setup,
        database_config=clients_config,
        datalake_config=clients_config,
    )

    return component
