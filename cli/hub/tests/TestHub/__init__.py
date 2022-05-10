import random
import time



class Main():

    def __init__(self,run_spec, *args, **kwargs):
        self.run_spec = run_spec
        self.test()

    def test(self):
        i = 0
        while True:
            print(self.run_spec)
            i+=1
            time.sleep(10)