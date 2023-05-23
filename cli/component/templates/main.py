import random
from typing import Type

import typer
from splight_lib.component import SplightBaseComponent
from splight_lib.execution import Task
from splight_lib.logging import getLogger
from splight_lib.models import Number

app = typer.Typer(pretty_exceptions_enable=False)
MyAsset = Type["MyAsset"]


class {{component_name}}(SplightBaseComponent):
    def __init__(self, component_id: str):
        super().__init__(component_id)
        self._logger = getLogger("MyComponent")

    def start(self):
        self.execution_engine.start(
            Task(
                handler=self._get_random_value,
                args=(self.input.min, self.input.max),
                period=self.input.period,
            )
        )

    def _get_random_value(self, min_value: float, max_value: float):
        value = (
            self.input.upper_bound - self.input.lower_bound
        ) * random.random() + self.input.lower_bound
        preds = Number(
            value=value,
        )
        preds.save()
        self._logger.info(f"\nValue = {value}\n")

    def command_myasset_print(self, my_asset: MyAsset):
        print("Command for MyAsset")

    def handle_myasset_create(self, my_asset: MyAsset):
        print("MyAsset create")

    def handle_myasset_delete(self, my_asset: MyAsset):
        print("MyAsset delete")


@app.command()
def main(component_id: str = typer.Option(...)):
    logger = getLogger("MyComponent")
    component = {{component_name}}(component_id=component_id)
    try:
        component.start()
    except Exception as exc:
        logger.exception(exc, tags="EXCEPTION")
        component.stop()


if __name__ == "__main__":
    app()
