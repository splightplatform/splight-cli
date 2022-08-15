import splight_models
from splight_lib import logging
from cli.utils import *


logger = logging.getLogger()


class Database:

    def __init__(self, context):
        self.context = context
        self.namespace = 'default'

    @property
    def client(self):
        return self.context.framework.setup.DATABASE_CLIENT(self.namespace)

    def list(self, obj_class):
        obj_class = getattr(splight_models, obj_class.title())
        return [
            i.dict()
            for i in self.client.get(obj_class)
        ]