import random
from typing import TypeVar
from splight_lib.component.algorithms import AbstractAlgorithmComponent
from splight_lib.execution import Task
from splight_lib import logging


logger = logging.getLogger()


# Custom Types
## NOTE: In case you want to create new instances of this Class
## You can find this model in self.custom_model.MyAsset inside the Main class
MyAsset = TypeVar('MyAsset')


class Main(AbstractAlgorithmComponent):
    # Starting point
    def start(self):
        self.my_assets = {}
        logger.info(f"Starting randomizer in range {self.input.min} - {self.input.max}")
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
        print(self.my_assets)

    # Bindings
    def handle_myasset_create(self, my_asset: MyAsset):
        self.my_assets[my_asset.id] = my_asset
        print("CREATED")

    def handle_myasset_delete(self, my_asset: MyAsset):
        try:
            del self.my_assets[my_asset.id]
        except KeyError:
            pass
        print("DELETED")

    # Commands
    def command_myasset_print(self, my_asset: MyAsset):
        print(my_asset)
        return my_asset.dict()
