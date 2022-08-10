import splight_models
from splight_lib import logging
from cli.utils import *
from cli.client import SplightClient, remotely_available
from cli.settings import setup


logger = logging.getLogger()


class Database(SplightClient):

    def __init__(self, context, namespace):
        self.context = context
        self.namespace = namespace if namespace is not None else 'default'
        self.user_handler = UserHandler(context)

    @remotely_available
    def list(self, obj_class):
        db_client = setup.DATABASE_CLIENT(self.namespace)
        obj_class = getattr(splight_models, obj_class.title())
        return [
            i.dict()
            for i in db_client.get(obj_class)
        ]