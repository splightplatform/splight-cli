from typing import Any, Dict, List


# FIXME: make this faster using a stack
def walk_dict(data: Dict, current=[]):
    result = []

    if isinstance(data, Dict):
        for key, value in data.items():
            current.append(key)
            result.extend(walk_dict(value, current.copy()))
            current.pop()
    elif isinstance(data, List):
        for index, item in enumerate(data):
            current.append(index)
            result.extend(walk_dict(item, current.copy()))
            current.pop()
    else:
        result.append((current.copy(), data))

    return result


def get_dict_value(path: List, data: Dict):
    # Assumes the path exists
    current = data
    for key in path:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[int(key)]
        else:
            raise ValueError(f"Invalid path: {path}")
    return current


def set_dict_value(value: Any, path: List, data: Dict):
    # Assumes the path exists
    current = data
    for key in path[:-1]:
        current = current[key]

    last_key = path[-1]

    if isinstance(current, dict):
        current[last_key] = value
    elif isinstance(current, list):
        current[int(last_key)] = value
    else:
        raise ValueError(f"Invalid path: {path}")
