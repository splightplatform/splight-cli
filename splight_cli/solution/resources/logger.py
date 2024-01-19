from colorama import Style
from typer import confirm

from splight_cli.solution.resources.base import Resource


class ResourceLogger:
    template = '{type}["{name}"]: {message} [id={id}]'

    @staticmethod
    def _bold(message: str) -> str:
        return f"{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def resource_info(self, message: str, resource: Resource):
        formatted_message = self.template.format(
            type=resource.type,
            name=resource.name,
            id=resource.id,
            message=message,
        )
        print(self._bold(formatted_message))

    def _event(
        self,
        message: str,
        previous_line: bool = False,
        new_line: bool = False,
        bold: bool = False,
    ):
        formatted_message = ""
        if previous_line:
            formatted_message += "\n"
        formatted_message += f"{self._bold(message)}" if bold else message
        if new_line:
            formatted_message += "\n"
        print(formatted_message)

    def no_changes(self):
        self._event(
            "No changes. Your infrastructure matches the configuration.",
            bold=True,
            previous_line=True,
            new_line=True,
        )
        self._event(
            "Splight has compared your real infrastructure against your configuration and found no differences, so no changes are needed.",
        )

    def plan(self):
        self._event(
            "Splight solution will perform the following actions:",
            previous_line=True,
            new_line=True,
        )
        # self._logger.print_diffs(diffs)
        # self._event(
        #     f"Plan: {len(self._to_create)} to add, {len(self._to_update)} to change, {len(self._to_delete)} to destroy."
        # )

    def apply(self):
        confirmation = confirm(
            """
            Do you want to perform these actions?
            Terraform will perform the actions described above.

            Enter a value:"""
        )
        return confirmation
