from splight_lib.component import AbstractComponent


class Main(AbstractComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test(self):
        print("HELLO2")

    def start(self):
        print("HELLO")
        self.test()
        self.terminate()

    def hello(self, message: str):
        return "hello" + message