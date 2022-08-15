from splight_models import StorageFile
from cli.utils import *


class Storage:

    def __init__(self, context):
        self.context = context
        self.namespace = 'default'
    
    @property
    def client(self):
        return self.context.framework.setup.STORAGE_CLIENT(self.namespace)

    def get(self):
        return self.client.get(StorageFile)

    def save(self, file, prefix):
        return self.client.save(StorageFile(file=file), prefix=prefix)
    
    def delete(self, file):
        return self.client.delete(StorageFile, id=file)
