import pandas as pd
from cli.utils import *
from splight_lib.database import DatabaseClient
from splight_lib.datalake import DatalakeClient
from splight_lib.shortcut import asset_load_history


class History():
    def __init__(self, context, namespace):
        self.context = context
        self.user_handler = UserHandler(context)
        self.namespace = namespace if namespace is not None else 'default'
        self.database_client = DatabaseClient(self.namespace)
        self.datalake_client = DatalakeClient(self.namespace)

    def load(self, asset_id, asset_name_cols, attribute_id, attribute_name_cols, file, example=False, remote=False):
        if example:
            raise NotImplementedError
        if remote:
            headers = self.user_handler.authorization_header
            data = {
                "attribute_id": attribute_id,
                "asset_id": asset_id,
                "attribute_name_cols": attribute_name_cols,
                "asset_name_cols": asset_name_cols,
            }
            files = {"file": open(file, 'rb')}
            response = api_post(f"{self.context.SPLIGHT_PLATFORM_API_HOST}/history/", data=data, files=files, headers=headers)
            if response.status_code != 201:
                raise Exception(f"Failed to push data to datalake: {response.text}")
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
