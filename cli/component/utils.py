from typing import Any, Dict, Optional, Tuple
from uuid import uuid4


def generate_component(
    json_spec: Dict[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    component_id = str(uuid4())
    component = {
        component_id: {
            "id": component_id,
            "name": json_spec.get("name"),
            "version": f"{json_spec['name']}-{json_spec['version']}",
            "custom_types": json_spec.get("custom_types", []),
            "component_type": json_spec.get("component_type", "connector"),
            "input": json_spec.get("input", []),
            "output": json_spec.get("output", []),
            "commands": json_spec.get("commands", []),
            "endpoints": json_spec.get("endpoints", []),
            "bindings": json_spec.get("bindings", []),
        }
    }
    return component_id, component


def generate_component_object(
    custom_type: Dict[str, Any],
    component_id: str,
    asset_id: Optional[str] = None,
    attribute_id: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    component_object_id = str(uuid4())
    # TODO: review description and type
    component_object = {
        component_object_id: {
            "id": component_object_id,
            "name": custom_type["name"],
            "component_id": component_id,
            "description": "",
            "type": custom_type["name"],
            "data": custom_type.get("fields", []),
        }
    }
    return component_object_id, component_object


def generate_asset(field: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    asset_id = str(uuid4())
    # TODO: review attributes
    asset = {
        asset_id: {
            "id": asset_id,
            "name": field["name"],
            "description": field.get("description"),
            "tags": [],
            "attributes": [],
            "verified": False,
            "geometry": None,
            "centroid": None,
            "external_id": None,
            "is_public": False,
        }
    }
    return asset_id, asset


def generate_attribute(field: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    attribute_id = str(uuid4())
    attribute = {
        attribute_id: {
            "id": attribute_id,
            "name": field["name"],
        }
    }
    return attribute_id, attribute
