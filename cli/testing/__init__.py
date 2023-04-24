import os

import pytest
from cli.component.loaders import ComponentLoader, SpecLoader


def get_tests_initial_setup() -> dict:
    # TODO: this will be change when we refactor setup.configure to don't override envvars
    return {
        "DATABASE_CLIENT": "splight_lib.client.database.LocalDatabaseClient",
        "DATALAKE_CLIENT": "splight_lib.client.datalake.LocalDatalakeClient",
        "NAMESPACE": "test",
        # TODO: uncomment following line when local communication client will be ready
        # "COMMUNICATION_CLIENT": "splight_lib.client.communication.LocalCommunicationClient"
    }


@pytest.fixture
def component(mocker):
    # we don't need execution client to run locally
    mocker.patch("splight_lib.component.abstract.ExecutionClient")
    mocker.patch(
        "splight_lib.client.datalake.LocalDatalakeClient.create_index"
    )

    # TODO: search a better and cleaner solution
    component_path = os.environ["COMPONENT_PATH_FOR_TESTING"]
    clients_config = {"path": component_path}
    # local database, datalake and communication clients
    initial_setup = get_tests_initial_setup()

    # TODO: remove, just temportal until define LocalCommunicationClient
    mocker.patch("remote_splight_lib.communication.client.CommunicationClient")
    initial_setup[
        "COMMUNICATION_CLIENT"
    ] = "splight_lib.client.datalake.LocalDatalakeClient"
    mocker.patch(
        "splight_lib.component.abstract.AbstractComponent._load_instance_kwargs_for_clients"
    )
    mocker.patch(
        "splight_lib.component.abstract.AbstractComponent.communication_client_kwargs",
        clients_config,
    )
    mocker.patch(
        "splight_lib.component.abstract.BindingsMixin._load_client_bindings"
    )

    component_loader = ComponentLoader(path=component_path)
    spec_loader = SpecLoader(path=component_path)

    component_class = component_loader.load()
    run_spec = spec_loader.load(input_parameters={}).dict()

    component = component_class(
        run_spec=run_spec,
        initial_setup=initial_setup,
        database_config=clients_config,
        datalake_config=clients_config,
    )

    return component
