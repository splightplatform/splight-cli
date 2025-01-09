from collections import namedtuple

from rich.console import Console
from rich.table import Table
from splight_lib.models import HubServer

console = Console()


class HubServerManager:
    def list_servers(self):
        servers_tuple = namedtuple("Server", ["name", "version"])
        all_servers = HubServer.list()
        servers = set(
            [
                servers_tuple(server.name, server.version)
                for server in all_servers
            ]
        )
        table = Table("Name", "Version", title="Hub Server List")
        [table.add_row(server.name, server.version) for server in servers]
        console.print(table)
