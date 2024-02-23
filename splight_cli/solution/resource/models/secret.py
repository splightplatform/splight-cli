from splight_lib.models import Secret as SecretSchema
from splight_lib.models.base import SplightDatabaseBaseModel

from splight_cli.solution.resource.models.base import Resource


# FIXME: After the first time this resource is created, the value will be saved
# unencrypted in the state.
# This can be fixed easily by overriding the create method and replacing the plain
# text value with the encrypted one inside de client.
# But it needs a fix from the splight_lib first, which is, that the model does not
# reinitialize itself with the API response after the '.save()'.
# In other words, the model does not contain the encrypted value after '.save()'
# A workaround is refreshing the resource after creation (see below) which achieves
# the same goal, but does one more request.
class Secret(Resource):
    _schema: SplightDatabaseBaseModel = SecretSchema

    def __init__(self, *args, **kwargs):
        # If this resource already is in the state/engine.
        if kwargs.get("id", False):
            arguments = kwargs.get("arguments")

            # Then encrypt the secret value to compare it with the value in the
            # state.
            client = self._schema(**arguments)
            arguments["value"] = client.decrypt(arguments["name"]).value

        super().__init__(*args, **kwargs)

    def create(self) -> None:
        client = self._schema(**self.arguments)
        client.save()
        self.id = client.id

        # NOTE: If this fails the state will be inconsistent,
        # better do the fix explained above
        self.refresh()  # Retrieve the encrypted value
