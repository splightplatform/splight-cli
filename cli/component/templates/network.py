from splight_lib.component.io import AbstractNetworkComponent

class Main(AbstractNetworkComponent):

    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
    
    def start(self):
        pass
