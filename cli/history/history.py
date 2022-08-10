import pandas as pd
from cli.client import SplightClient, remotely_available
from cli.utils import *
from splight_lib.shortcut import asset_load_history


class History(SplightClient):
    def __init__(self, context, namespace):
        self.context = context
        self.user_handler = UserHandler(context)
        self.namespace = namespace if namespace is not None else 'default'

    @remotely_available
    def load(self, asset_id, asset_name_cols, attribute_id, attribute_name_cols, file, example=False):
        self.database_client = self.DATABASE_CLIENT(self.namespace)
        self.datalake_client = self.DATALAKE_CLIENT(self.namespace)
        if example:
            raise NotImplementedError
        else:
            dataframe = pd.read_csv(file)
            return asset_load_history(
                dataframe=dataframe,
                db_client=self.database_client,
                dl_client=self.datalake_client,
                asset_id=asset_id,
                asset_name_cols=asset_name_cols,
                attribute_id=attribute_id,
                attribute_name_cols=attribute_name_cols
            )
