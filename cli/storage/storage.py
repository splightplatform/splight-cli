from cli.utils import *
from splight_lib.storage import StorageClient
from splight_models import StorageFile


class Storage():

    def __init__(self, context, namespace):
        self.context = context
        self.namespace = namespace
        self.client = StorageClient(namespace)

    def get(self):
        return self.client.get(StorageFile)

    def save(self, file):
        return self.client.save(StorageFile(file=file))
    
    def delete(self, file):
        return self.client.delete(StorageFile, id=file)
