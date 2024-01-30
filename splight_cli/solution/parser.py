import re
from typing import Dict, List, Optional

import yaml

from splight_cli.solution.dict import walk_dict


class DuplicateResourceError(Exception):
    pass


def parse_reference(value: str) -> Optional[Dict]:
    """Return the reference if it matches the regex or None otherwise"""

    # Only process strings
    if isinstance(value, str):
        # Building this with format strings breaks the expression
        pattern = r"^\${{(Asset|File|Function)\.(\w+)((?:\.\w+)+)}}$"

        # Get the matches
        match = re.match(pattern, value)

        if match:
            type, name, path = match.groups()

            # The capturing group for path starts with a leading dot,
            # so we remove it
            path = path.lstrip(".").split(".")

            # Cast the digit keys (array indexes)
            path = [int(key) if key.isdigit() else key for key in path]

            key = f"{type}:{name}"

            return key, path


class Parser:
    def __init__(self, spec_file: str) -> None:
        try:
            with open(spec_file, "r") as fp:
                self._spec_file_data = yaml.safe_load(fp)
        except FileNotFoundError:
            raise Exception(f"Spec file '{spec_file}' not found.")

    def parse(self) -> List[Dict]:
        # Here we build the dependency graph using the resource keys
        dependency_graph = {}

        specs = {}
        for resource_spec in self._spec_file_data:
            name = resource_spec["name"]
            type = resource_spec["type"]
            arguments = resource_spec["arguments"]

            # Parse each resource leaf value to see if its a reference
            depends_on = set({})
            references = []
            for path, value in walk_dict(resource_spec["arguments"]):
                result = parse_reference(value)
                if result is not None:
                    key, source = result

                    reference = {
                        "key": key,  # Key of the referenced resource
                        "source": source,  # Where to get the value
                        "target": path,  # Where to put the value
                        "string": value,  # The string value of the reference
                    }

                    references.append(reference)
                    depends_on.add(key)

            key = f"{type}:{name}"
            if key in specs:
                raise DuplicateResourceError(
                    f"Resource '{name}' of type '{type}' is defined twice."
                )

            specs[key] = {
                "name": name,
                "type": type,
                "depends_on": list(depends_on),
                "references": references,
                "arguments": arguments,
            }

            # Add its dependecies to the graph
            dependency_graph[key] = depends_on

        return specs, dependency_graph
