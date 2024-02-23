from colorama import Style


class ResourceLogger:
    template = '{type}["{name}"]: {message} [id={id}]'

    @staticmethod
    def _bold(message: str) -> str:
        return f"{Style.BRIGHT}{message}{Style.RESET_ALL}"

    def resource(self, message: str, resource):
        formatted_message = self.template.format(
            type=resource.type,
            name=resource.name,
            id=resource.id,
            message=message,
        )
        print(self._bold(formatted_message))

    def event(
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

    def diff(self, diff):
        print("\n".join(diff))
