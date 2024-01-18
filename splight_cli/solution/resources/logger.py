from rich.console import Console
from rich.style import Style

console = Console()
style = Style(bold=True)


# TODO: deberia estar en el repr esto?
class ResourceLogger:
    BASE_MESSAGE = '{type}["{name}"]: %s [id={id}]'

    def __init__(
        self, resource_type: str, resource_name: str, resource_id: str
    ):
        self.base_msg = self.BASE_MESSAGE.format(
            type=resource_type,
            name=resource_name,
            id=resource_id,
        )

    def read_start(self):
        console.print(self.base_msg % "Reading...", style=style)

    def read_complete(self, elapsed_time):
        console.print(
            self.base_msg % f"Read complete after {elapsed_time:.2f} seconds",
            style=style,
        )

    def refreshing_state(self):
        console.print(self.base_msg % "Refreshing state...", style=style)

    def diff(self):
        pass


# def diff_json_objects(obj1, obj2):
#     stack = [("", obj1, obj2)]
#
#     while stack:
#         path, o1, o2 = stack.pop()
#
#         for key in o1:
#             if key not in o2:
#                 print(f"- {path}.{key} will be removed")
#             else:
#                 if isinstance(o1[key], dict) and isinstance(o2[key], dict):
#                     stack.append((f"{path}.{key}", o1[key], o2[key]))
#                 elif o1[key] != o2[key]:
#                     print(f"  # {path}.{key} will be updated")
#                     print(f"  - {key} = {o1[key]}")
#                     print(f"  + {key} = {o2[key]}")
#
#         for key in o2:
#             if key not in o1:
#                 print(f"+ {path}.{key} will be created")
#
# # Example usage
# json_obj1 = {
#     "module": {
#         "components": {
#             "module": {
#                 "github_resources": {
#                     "github_repository": {
#                         "settings": {
#                             "name": "old_name",
#                             "allow_merge_commit": True,
#                             "visibility": "public"
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }
#
# json_obj2 = {
#     "module": {
#         "components": {
#             "module": {
#                 "github_resources": {
#                     "github_repository": {
#                         "settings": {
#                             "name": "new_name",
#                             "allow_merge_commit": False,
#                             "visibility": "private"
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }
#
# diff_json_objects(json_obj1, json_obj2)
