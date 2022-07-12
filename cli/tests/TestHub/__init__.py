from splight_lib.component import AbstractAlgorithmComponent
class Main(AbstractAlgorithmComponent):
    def __init__(self, run_spec, *args, **kwargs):
        self.run_spec = run_spec
        self.test()

    def test(self):
        print(self.run_spec)