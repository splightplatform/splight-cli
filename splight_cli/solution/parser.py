import re
from typing import Dict, List, Optional

import yaml


class DuplicateResourceError(Exception):
    pass


def walk(data: Dict, current=[]):
    result = []

    if isinstance(data, Dict):
        for key, value in data.items():
            current.append(key)
            result.extend(walk(value, current.copy()))
            current.pop()
    elif isinstance(data, List):
        for index, item in enumerate(data):
            current.append(index)
            result.extend(walk(item, current.copy()))
            current.pop()
    else:
        result.append((current.copy(), data))

    return result


def get_value(data, path):
    current = data
    for key in path:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[int(key)]
        else:
            raise ValueError(f"Invalid path: {path}")
        return current


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
                self._data = yaml.safe_load(fp)
        except FileNotFoundError:
            raise Exception(f"Spec file '{spec_file}' not found.")

    def parse(self) -> List[Dict]:
        # Here we build the dependency graph using the resource keys
        dependency_graph = {}

        resources = {}
        for resource_spec in self._data:
            name = resource_spec["name"]
            type = resource_spec["type"]
            arguments = resource_spec["arguments"]

            # Parse each resource leaf value to see if its a reference
            depends_on = []
            for path, value in walk(resource_spec):
                result = parse_reference(value)
                if result is not None:
                    key, source = result

                    reference = {
                        "key": key,  # Key of the referenced resource
                        "source": source,  # Where to get the value
                        "target": path,  # Where to put the value
                    }

                    depends_on.append(reference)

            key = f"{type}:{name}"
            if key in resources:
                raise DuplicateResourceError(
                    f"Resource '{name}' of type '{type}' is defined twice."
                )

            resources[key] = {
                "name": name,
                "type": type,
                "depends_on": depends_on,
                "arguments": arguments,
            }

            # Add its dependecies to the graph
            dependency_graph[key] = set({})
            for reference in depends_on:
                dependency_graph[key].add(reference["key"])

        return resources, dependency_graph
