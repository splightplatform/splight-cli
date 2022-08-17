from splight_lib import logging
from splight_models import Deployment
from cli.utils import *
from cli.constants import DEFAULT_NAMESPACE

logger = logging.getLogger()


class DeploymentHandler:

    def __init__(self, context):
        self.context = context
        self.namespace = DEFAULT_NAMESPACE

    @property
    def client(self):
        return self.context.framework.setup.DEPLOYMENT_CLIENT(self.namespace)

    def list(self):
        return [
            i.dict()
            for i in self.client.get(Deployment)
        ]