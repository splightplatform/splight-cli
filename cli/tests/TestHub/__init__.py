from splight_lib.component import AbstractAlgorithmComponent


class Main(AbstractAlgorithmComponent):
    def test(self):
        print("HELLO2")

    def start(self):
        print("HELLO")
        self.test()
        self.terminate()
