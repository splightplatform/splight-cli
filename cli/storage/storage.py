from splight_models import StorageFile
from cli.client import SplightClient, remotely_available
from cli.utils import *
from cli.settings import setup


class Storage(SplightClient):

    def __init__(self, context, namespace):
        self.context = context
        self.namespace = namespace if namespace is not None else 'default'

    @remotely_available
    def get(self):
        client = setup.STORAGE_CLIENT(self.namespace)
        return client.get(StorageFile)

    @remotely_available
    def save(self, file, prefix):
        client = setup.STORAGE_CLIENT(self.namespace)
        return client.save(StorageFile(file=file), prefix=prefix)
    
    @remotely_available
    def delete(self, file):
        client = setup.STORAGE_CLIENT(self.namespace)
        return client.delete(StorageFile, id=file)
