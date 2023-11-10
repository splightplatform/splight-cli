from typing import Type

from cli.solution.utils import SplightTypes, bprint, confirm_or_yes


class Destroyer:
    def __init__(self, plan, yes_to_all: bool):
        self._plan = plan
        self._yes_to_all = yes_to_all

    def destroy(
        self, model: Type[SplightTypes], instance_to_delete: SplightTypes
    ) -> bool:
        """Destroys the state instance passed.

        Parameters
        ----------
        model : Type[SplightTypes]
            A splight type.
        instance_to_delete : SplightTypes
            The instance to be deleted.

        Returns
        -------
        bool
            True if it was confirmed and deleted, False instead.
        """
        model_name = model.__name__
        bprint(f"You are about to destroy the following {model_name}:")
        bprint(instance_to_delete)
        confirm = confirm_or_yes(self._yes_to_all, "Are you sure?")
        if confirm:
            instance_to_delete.delete()
            return True
        return False
