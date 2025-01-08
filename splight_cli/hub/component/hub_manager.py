from rich.console import Console
from rich.table import Table
from splight_lib.models import HubComponent

console = Console()


class HubComponentManager:
    def list_components(self):
        components = HubComponent.list(limit_=10000)
        names = set([component.name for component in components])
        table = Table("Name")
        [table.add_row(name) for name in names]
        console.print(table)

    def versions(self, name: str):
        components = HubComponent.list(name=name)
        table = Table("Name", "Version", "Verification", "Privacy Policy")
        for item in components:
            table.add_row(
                name, item.version, item.verification, item.privacy_policy
            )
        console.print(table)
