import random
from typing import TypeVar
from splight_lib.component import AbstractComponent
from splight_lib.execution import Task
from splight_lib import logging

# Logging tool
logger = logging.getLogger()

# Custom Types
## NOTE: In case you want to create new instances of this Class
## You can find this model in self.custom_model.MyAsset inside the Main class
MyAsset = TypeVar('MyAsset')


class Main(AbstractComponent):

    # Init
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_assets = {
            item.id: item
            for item in self.database_client.get(self.custom_types.MyAsset)
        }
        logger.info(f"Starting randomizer in range {self.input.min} - {self.input.max}")

    # Starting point
    def start(self):
        self.execution_client.start(
            Task(handler=self._give_a_random_number, args=(self.input.min, self.input.max), period=self.input.period)
        )
        self.execution_client.start(
            Task(handler=self._list_assets, args=(), period=self.input.period)
        )

    # Periodic Tasks
    def _give_a_random_number(self, min, max):
        chosen_number = random.randint(min, max)
        logger.info(f"Random number: {chosen_number}")
        out = self.output.Value(value=chosen_number)
        self.datalake_client.save(instances=[out])

    def _list_assets(self):
        logger.info(f"List of myassets: List[MyAsset] {self.my_assets}")

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
    def command_myasset_print(self, myasset: MyAsset):
        logger.info(f"PRINTED MyAsset: {myasset}")
        return myasset.dict()