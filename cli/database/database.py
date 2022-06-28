from cli.utils import *
from splight_lib.database import DatabaseClient
from datetime import datetime
import splight_models as models
import pandas as pd


class Database():

    def __init__(self, context, namespace):
        self.context = context
        self.namespace = namespace if namespace is not None else 'default'
        self.user_handler = UserHandler(context)
        self.db_client = DatabaseClient(self.namespace)
    
    def _list_remote(self, obj_class):
        headers = self.user_handler.authorization_header
        page = api_get(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/{obj_class.lower()}/", headers=headers)
        page = page.json()
        results = []
        if page["results"]:
            results.extend(page["results"])
        while page["next"] is not None:
            page = api_get(page["next"], headers=headers)
            page = page.json()
            if page["results"]:
                results.extend(page["results"])
        return results

    def list(self, obj_class, remote):
        import splight_models
        if remote:
            items = self._list_remote(obj_class)
        else:
            obj_class = getattr(splight_models, obj_class)
            items = [{"id": i.id, "name": i.name} for i in self.db_client.get(obj_class)]
        return items