from splight_lib.component.io import AbstractClientComponent
from splight_lib.communication import Variable
from typing import List

class Main(AbstractClientComponent):

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)

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