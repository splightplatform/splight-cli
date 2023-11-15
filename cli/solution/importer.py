from collections import namedtuple
from uuid import UUID

from rich.console import Console
from splight_lib.models import Asset, Component, RoutineObject

from cli.solution.models import ElementType, PlanSolution, StateSolution
from cli.solution.utils import IMPORT_PREFIX

ImportResult = namedtuple("ImportResult", ("was_imported", "plan", "state"))

console = Console()


class ImporterExecutor:
    def __init__(self, plan: PlanSolution, state: StateSolution):
        self._plan = plan
        self._state = state
        self._map_element_to_model = {"asset": Asset, "component": Component}

    def import_element(self, element: ElementType, id: UUID) -> ImportResult:
        """Imports an element and saves it to both the plan and state file.

        Parameters
        ----------
        element : ElementType
            Either 'asset' or 'component'.
        id : UUID
            The UUID of the element we want to import.

        Returns
        -------
        Tuple[Solution, Solution]
            The updated plan and state.
        """
        console.print(f"\nImporting {element} with id {id} ...", style="bold")
        if self._is_already_imported(element, id):
            console.print(
                f"{element} with id {id} is already in the state file. "
                "Skipping...",
                style="bold",
            )
            return ImportResult(
                was_imported=False,
                plan=self._plan,
                state=self._state,
            )
        model = self._map_element_to_model[element]
        retrieved_elem = model.retrieve(resource_id=id)
        if element == ElementType.component:
            retrieved_elem.routines = RoutineObject.list(component_id=id)

        plan_import_elems = getattr(self._plan, f"{IMPORT_PREFIX}{element}s")
        plan_import_elems.append(retrieved_elem)

        state_import_elems = getattr(self._state, f"{IMPORT_PREFIX}{element}s")
        state_import_elems.append(retrieved_elem)

        return ImportResult(
            was_imported=True, plan=self._plan, state=self._state
        )

    def _is_already_imported(self, element: ElementType, id: UUID) -> bool:
        state_imported = getattr(self._state, f"{IMPORT_PREFIX}{element}s")
        state_non_imported = getattr(self._state, f"{element}s")
        for state_elem in state_imported + state_non_imported:
            if state_elem.id == str(id):
                return True
        return False
