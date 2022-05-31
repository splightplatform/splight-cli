import random
import time
from splight_lib.component import AbstractAlgorithmComponent



class Main(AbstractAlgorithmComponent):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test()

    def test(self):
        i = 0
        while True:
            print(self.int)
            i+=1
            time.sleep(10)