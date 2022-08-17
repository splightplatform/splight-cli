from splight_lib.component.io import AbstractServerComponent
from splight_models import Variable
from typing import List

class Main(AbstractServerComponent):

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)

    def handle_update(self, variables: List[Variable]) -> None:
        '''
        Implement this method to handle update requests.
        Args:
            variables: List of variables to update.
        '''
        pass

    def start(self):
        pass