from splight_lib import logging
from splight_lib.component.algorithms import AbstractAlgorithmComponent
from splight_lib.execution import Task


logger = logging.getLogger()


class Main(AbstractAlgorithmComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"It worked!")

    def start(self):
        pass
        # To start a periodic function uncomment this
        # self.execution_client.start(
        #     Task(handler=self._my_periodic_function, args=tuple(), period=self.period)
        # )

    def _my_periodic_function(self):
        logger.info(f"It worked!")
        # To ingest in datalake uncomment the following
        # args = {
        #     "value": chosen_number,
        # }
        # self.datalake_client.save(
        #     Variable,
        #     instances=[Variable(args=args)],
        #     collection=self.collection_name
        # )
