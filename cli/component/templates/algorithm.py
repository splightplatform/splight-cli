import random
from typing import Optional
from pydantic import BaseModel
from splight_lib.component.algorithms import AbstractAlgorithmComponent
from splight_lib.execution import Task
from splight_lib import logging
from splight_models import Asset


logger = logging.getLogger()


# Custom Types
class MyAsset(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    asset: Asset
    alias: str


class Main(AbstractAlgorithmComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_assets = {}
        logger.info(f"Starting randomizer in range {self.input.min} - {self.input.max}")

    def start(self):
        # Starting point
        self.execution_client.start(
            Task(handler=self._give_a_random_number, args=(self.input.min, self.input.max), period=self.input.period)
        )
        self.execution_client.start(
            Task(handler=self._list_assets, args=(), period=self.input.period)
        )

    # Tasks
    def _give_a_random_number(self, min, max):
        chosen_number = random.randint(min, max)
        logger.info(f"Random number: {chosen_number}")
        out = self.output.Value(value=chosen_number)
        self.datalake_client.save(instances=[out], collection=self.collection_name)

    def _list_assets(self):
        logger.info(f"MyAssets: {self.my_assets}")

    # Bindings
    def handle_myasset_create(self, my_asset: MyAsset):
        self.my_assets[my_asset.id] = my_asset
        logger.info(f"CREATED MyAsset: {my_asset}")

    def handle_myasset_delete(self, my_asset: MyAsset):
        try:
            logger.info(f"DELETED MyAsset: {my_asset}")
            del self.my_assets[my_asset.id]
        except KeyError:
            pass

    # Commands
    def command_myasset_print(self, asset: MyAsset):
        logger.info(f"PRINTED MyAsset: {asset}")
        return asset.dict()