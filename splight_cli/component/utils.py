from typing import Any, Dict, Tuple
from uuid import uuid4

from splight_lib.models import Asset, Attribute, Component, ComponentObject


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
            "endpoints": json_spec.get("endpoints", []),
        }
    }
    return component_id, component


def generate_component_object(
    custom_type: Dict[str, Any],
    component_id: str,
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


def db_from_spec(json_spec):
    component_db = {
        model.__name__.lower(): {}
        for model in [Asset, Attribute, Component, ComponentObject]
    }
    component_id, component_db["component"] = generate_component(json_spec)
    for custom_type in json_spec.get("custom_types"):
        for field in custom_type.get("fields"):
            if field["type"] == "Asset":
                asset_id, asset = generate_asset(field)
                component_db["asset"].update(asset)
                field.update({"value": asset_id})
            elif field["type"] == "Attribute":
                attribute_id, attribute = generate_attribute(field)
                component_db["attribute"].update(attribute)
                field.update({"value": attribute_id})
        _, component_object = generate_component_object(
            custom_type, component_id
        )
        component_db["componentobject"].update(component_object)
    return component_db


def fake_asset():
    asset_id = str(uuid4())
    return {
        asset_id: {
            "id": asset_id,
            "name": "fake_asset_name",
            "description": "fake description",
            "tags": [],
            "attributes": [],
            "verified": False,
            "geometry": None,
            "centroid": None,
            "external_id": None,
            "is_public": False,
        }
    }


def fake_attribute():
    attribute_id = str(uuid4())
    return {
        attribute_id: {
            "id": attribute_id,
            "name": "fake_attr_name",
        }
    }
