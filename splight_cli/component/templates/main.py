import random
from typing import Optional, Type

import typer
from splight_lib.component import SplightBaseComponent
from splight_lib.execution import Task
from splight_lib.logging import getLogger
from splight_lib.models import Number

app = typer.Typer(pretty_exceptions_enable=False)


class {{component_name}}(SplightBaseComponent):
    def __init__(self, component_id: str):
        super().__init__(component_id)
        self._logger = getLogger("MyComponent")

    def start(self):
        self.execution_engine.start(
            Task(
                handler=self._run,
                args=(self.input.min, self.input.max),
                period=self.input.period,
            )
        )

    def _run(self, min_value: float, max_value: float):
        value = self._give_a_random_value(
            self.input.lower_bound, self.input.upper_bound
        )
        preds = Number(
            value=value,
        )
        preds.save()
        self._logger.info(f"\nValue = {value}\n")

    def _give_a_random_value(self, min: float, max: float) -> float:
        return (max - min) * random.random() + min


@app.command()
def main(
    component_id: str = typer.Option(...),
    input: Optional[str] = typer.Option(None),
):
    logger = getLogger("MyComponent")
    component = {{component_name}}(component_id=component_id)
    try:
        component.start()
    except Exception as exc:
        logger.exception(exc, tags="EXCEPTION")
        component.stop()


if __name__ == "__main__":
    app()
