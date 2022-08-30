from splight_lib.component.io import AbstractClientComponent
from splight_models import Variable
from typing import List

class Main(AbstractClientComponent):

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)

    def start(self):
        pass
        # To start a periodic function uncomment this
        # self.execution_client.start(
        #     Task(handler=self._my_periodic_function, args=tuple(), period=self.period)
        # )

    def handle_write(self, variables: List[Variable]) -> None:
        '''
        Implement this method to handle write requests.
        Args:
            variables: List of variables to write to device.
        '''
        pass

    def handle_subscribe(self, variables: List[Variable]) -> None:
        '''
        Implement this method to handle subscribe requests.
        Args:
            variables: List of variables to subscribe to.
        '''
        pass

    def handle_unsubscribe(self, variables: List[Variable]):
        '''
        Implement this method to handle unsubscribe requests.
        Args:
            variables: List of variables to unsubscribe from.
        '''
        pass