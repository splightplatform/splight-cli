from splight_lib.component import AbstractAlgorithmComponent


class Main(AbstractAlgorithmComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start()

    def test(self):
        print("HELLO2")

    def start(self):
        print("HELLO")
        self.test()
        self.terminate()
