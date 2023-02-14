class InvalidSplightCLIVersion(Exception):
    def __init__(self, component_cli_version: str, cli_version: str):
        self._msg = (
            f"Component uses splight cli version {component_cli_version} but "
            f"should be {cli_version}"
        )

    def __str__(self) -> str:
        return self._msg

class ReadmeExists(Exception):
    def __init__(self, readme_path: str):
        self._msg = (
            f"\nReadme already exists at {readme_path}"
            f"\nRemove it or use --force to overwrite it"
        )

    def __str__(self) -> str:
        return self._msg