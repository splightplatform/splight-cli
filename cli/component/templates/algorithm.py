import random
from splight_lib.component.algorithms import AbstractAlgorithmComponent
from splight_lib.execution import Task
from splight_lib import logging


logger = logging.getLogger()


class Main(AbstractAlgorithmComponent):

    # Init
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_assets = {}
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
        self.datalake_client.save(instances=[out], collection=self.collection_name)

    def _list_assets(self):
        logger.info(f"My List[self.custom_type.MyAsset]: {self.my_assets}")

    # Bindings
    def handle_myasset_create(self, my_asset):
        self.my_assets[my_asset.id] = my_asset
        logger.info(f"CREATED self.custom_type.MyAsset: {my_asset}")

    def handle_myasset_delete(self, my_asset):
        try:
            logger.info(f"DELETED self.custom_type.MyAsset: {my_asset}")
            del self.my_assets[my_asset.id]
        except KeyError:
            pass

    # Commands
    def command_myasset_print(self, myasset):
        logger.info(f"PRINTED self.custom_type.MyAsset: {myasset}")
        return myasset.dict()