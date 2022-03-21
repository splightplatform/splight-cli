from splight_lib.component.io import AbstractServerComponent
from splight_lib.communication import Variable
from typing import List

class {{component_name}}(AbstractServerComponent):

    def __init__(self, *args, **kwargs):
        super({{component_name}}, self).__init__(*args, **kwargs)

    def handle_update(self, variables: List[Variable]) -> None:
        '''
        Implement this method to handle update requests.
        Args:
            variables: List of variables to update.
        '''
        pass