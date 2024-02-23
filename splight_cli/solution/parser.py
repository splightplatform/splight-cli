import re
from typing import Dict, List, Optional

import yaml

from splight_cli.solution.dict import walk_dict


class DuplicateResourceError(Exception):
    pass


def parse_reference(value: str) -> Optional[Dict]:
    """Return the reference if it matches the regex or None otherwise"""
    # FIXME: make it so we are able to reference the 'name' of a resource.
    # This is super easy to do:
    # 1. Add '.id' and '.name' at the end of the regex
    # 2. Save that accessor to the references dict in each spec.
    # 3. Change the 'replace_references' function in ResourceManager so it
    #    gets the correct attribute.

    # Only process strings
    if isinstance(value, str):
        # Building this with format strings breaks the expression
        pattern = r"^\${{(Asset|Attribute|Metadata|File|Function|Secret|Alert|Component|Routine)\.(\w+)}}$"

        # Get the matches
        match = re.match(pattern, value)

        if match:
            type, name = match.groups()
            key = f"{type}:{name}"
            return key


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

        # - Does not destroy all elements.
        specs = {}
        for resource_spec in self._spec_file_data or []:
            name = resource_spec["name"]
            type = resource_spec["type"]
            arguments = resource_spec["arguments"]

            # Parse each resource leaf value to see if its a reference
            depends_on = set({})
            references = []
            for path, value in walk_dict(resource_spec["arguments"]):
                result = parse_reference(value)
                if result is not None:
                    key = result

                    # Must be done here, otherwise it would affect the dependency graph.
                    # Paths and values are validated later on, since we may need data
                    # that is available after creation.
                    # This also prevents trying to delete a resource which has another
                    # one referencing it.
                    # Also prevents self-referencing.
                    if key not in specs:
                        raise ValueError(
                            f"Reference '{value}' in resource '{name}' of type '{type}' points to a non existing resource."
                        )

                    reference = {
                        "key": key,  # Key of the referenced resource
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

        # NOTE: Before adding/changing features of the parser, insert a breakpoint
        # here and inspect the specs and dependency_graph objects, to see the shape
        # of the objects that the rest of the code needs.
        return specs, dependency_graph
