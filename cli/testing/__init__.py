import pytest
import os
import datetime
from typing import List, Dict

from cli.component.loaders import ComponentLoader, SpecLoader
from splight_models import (
    Component,
    Asset,
    Attribute,
    File,
    Query,
    QuerySourceType,
)
from splight_lib.client.database.local_client import LocalDatabaseClient


FAKE_VALUES_BY_TYPE = {
    # native types
    "int": 1,
    "bool": True,
    "str": "fake",
    "float": 5.5,
    "datetime": datetime.datetime(2022, 12, 18),
    "url": "www.google.com",
    # database types
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
        "DATABASE_CLIENT":
            "splight_lib.client.database.local_client.LocalDatabaseClient",
        "DATALAKE_CLIENT":
            "splight_lib.client.datalake.local_client.LocalDatalakeClient",
        "NAMESPACE": "test",
    }


def get_custom_type(custom_types: List[Dict], type_: str) -> str:
    # we need to create a custom object into the local db and return its id
    """
    setup = get_tests_initial_setup()
    clients_config = {"path": os.environ["COMPONENT_PATH_FOR_TESTING"]}
    db = LocalDatabaseClient(namespace=setup["NAMESPACE"], **clients_config)
    # TODO: load item as python class on instance variable
    item = [item for item in custom_types if item["name"] == type_][0]
    instance = ""
    saved_instance = db.save(instance)
    return saved_instance.id
    """
    return ["c69a7c55-8347-413d-9ad4-856278abb11f"]


def get_input_parameters(raw_spec: Dict) -> List[Dict]:
    custom_types = raw_spec.get("custom_types")
    inputs = raw_spec.get("input")
    for param in inputs:
        value = param.get("value")
        if value is None:
            type_ = param.get("type")
            if type_ in [ct["name"] for ct in custom_types]:
                
                value = get_custom_type(custom_types, type_)
            else:  # in splight_models.SIMPLE_TYPES
                value = FAKE_VALUES_BY_TYPE.get(type_)
            param.update({"value": value})
    return inputs


@pytest.fixture
def component(mocker):
    # TODO: search a better and cleaner solution
    component_path = os.environ["COMPONENT_PATH_FOR_TESTING"]
    clients_config = {"path": component_path}

    # local database, datalake and communication clients
    initial_setup = get_tests_initial_setup()

    mocker.patch("splight_lib.component.abstract.ExecutionClient")
    mocker.patch(
        "splight_lib.client.datalake.LocalDatalakeClient.create_index"
    )
    mocker.patch(
        "splight_lib.component.abstract.BindingsMixin._load_client_bindings"
    )
    mocker.patch(
        "splight_lib.component.abstract.AbstractComponent."
        "_load_instance_kwargs_for_clients"
    )
    mocker.patch(
        "splight_lib.component.abstract.AbstractComponent."
        "communication_client_kwargs",
        clients_config,
    )

    # TODO: remove, just temporal until define LocalCommunicationClient
    # #########################################################################
    mocker.patch("remote_splight_lib.communication.client.CommunicationClient")
    initial_setup[
        "COMMUNICATION_CLIENT"
    ] = "splight_lib.client.datalake.LocalDatalakeClient"
    # #########################################################################

    component_loader = ComponentLoader(path=component_path)
    spec_loader = SpecLoader(path=component_path)

    input_parameters = get_input_parameters(spec_loader.raw_spec)
    component_class = component_loader.load()
    # we need to pass input parameters with values
    run_spec = spec_loader.load(
        input_parameters=input_parameters, prompt_input=False
    )

    component = component_class(
        run_spec=run_spec.dict(),
        initial_setup=initial_setup,
        database_config=clients_config,
        datalake_config=clients_config,
    )

    return component
