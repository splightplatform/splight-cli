class InvalidSplightCLIVersion(Exception):
    def __init__(self, component_cli_version: str, cli_version: str):
        self._msg = (
            f"Component uses splight cli version {component_cli_version} but "
            f"should be {cli_version}"
        )

    def __str__(self) -> str:
        return self._msg
