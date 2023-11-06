from copy import deepcopy

from cli.solution.solution import StateSolution
from cli.solution.utils import to_dict

TEST_PLAN = {
    "assets": [
        {
            "attributes": [
                {
                    "asset": None,
                    "id": None,
                    "name": "attr_1",
                    "type": "Number",
                },
                {
                    "asset": None,
                    "id": None,
                    "name": "attr_2",
                    "type": "Number",
                },
                {
                    "asset": None,
                    "id": None,
                    "name": "attr_3",
                    "type": "Number",
                },
                {
                    "asset": None,
                    "id": None,
                    "name": "attr_4",
                    "type": "Number",
                },
            ],
            "centroid_coordinates": None,
            "description": None,
            "external_id": None,
            "geometry": None,
            "id": None,
            "is_public": False,
            "name": "test_asset",
            "tags": [],
            "verified": False,
        }
    ],
    "components": [
        {
            "bindings": [],
            "commands": [],
            "component_type": "algorithm",
            "custom_types": [],
            "endpoints": [],
            "id": None,
            "input": [],
            "name": "test_forecast",
            "output": [],
            "routines": [
                {
                    "component_id": None,
                    "config": [
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "period",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 86400,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "model",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": "XGB",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "percentile",
                            "required": False,
                            "sensitive": False,
                            "type": "float",
                            "value": None,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "frequency",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": "H",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "lags",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 256,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "tune_model",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": True,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "future_preds",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 168,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "training_data_limit",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 5000,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "zero_floor_clip",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": "yes",
                        },
                    ],
                    "description": "",
                    "id": None,
                    "input": [
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "target",
                            "required": True,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": {
                                "asset": "local.{{test_asset}}",
                                "attribute": "attr_1",
                            },
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": True,
                            "name": "past_extra_features",
                            "required": True,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": True,
                            "name": "future_extra_features",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": [
                                {
                                    "asset": "local.{{test_asset}}",
                                    "attribute": "attr_2",
                                },
                                {
                                    "asset": "local.{{test_asset}}",
                                    "attribute": "attr_3",
                                },
                            ],
                            "value_type": "Number",
                        },
                    ],
                    "name": "forecast_routine",
                    "output": [
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "predictions",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": {
                                "asset": "local.{{test_asset}}",
                                "attribute": "attr_4",
                            },
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "MAE",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "MAPE",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "R2",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                    ],
                    "status": "running",
                    "type": "ForecastRoutine",
                }
            ],
            "version": "LightSplightForecaster-1.0.3",
        }
    ],
    "imported_assets": [],
    "imported_components": [],
}
TEST_STATE_FILLED = {
    "assets": [
        {
            "attributes": [
                {
                    "asset": None,
                    "id": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                    "name": "attr_1",
                    "type": "Number",
                },
                {
                    "asset": None,
                    "id": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                    "name": "attr_2",
                    "type": "Number",
                },
                {
                    "asset": None,
                    "id": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                    "name": "attr_3",
                    "type": "Number",
                },
                {
                    "asset": None,
                    "id": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                    "name": "attr_4",
                    "type": "Number",
                },
            ],
            "centroid_coordinates": None,
            "description": None,
            "external_id": None,
            "geometry": None,
            "id": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
            "is_public": False,
            "name": "test_asset",
            "tags": [],
            "verified": False,
        }
    ],
    "components": [
        {
            "bindings": [],
            "commands": [],
            "component_type": "algorithm",
            "custom_types": [],
            "endpoints": [],
            "id": "5fcca841-8e80-4f5f-b941-763353c30e9b",
            "input": [],
            "name": "test_forecast",
            "output": [],
            "routines": [
                {
                    "component_id": "5fcca841-8e80-4f5f-b941-763353c30e9b",
                    "config": [
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "period",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 86400,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "model",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": "XGB",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "percentile",
                            "required": False,
                            "sensitive": False,
                            "type": "float",
                            "value": None,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "frequency",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": "H",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "lags",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 256,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "tune_model",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": True,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "future_preds",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 168,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "training_data_limit",
                            "required": False,
                            "sensitive": False,
                            "type": "int",
                            "value": 5000,
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "zero_floor_clip",
                            "required": False,
                            "sensitive": False,
                            "type": "str",
                            "value": "yes",
                        },
                    ],
                    "description": "",
                    "id": "j1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                    "input": [
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "target",
                            "required": True,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": {
                                "asset": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                                "attribute": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                            },
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": True,
                            "name": "past_extra_features",
                            "required": True,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": True,
                            "name": "future_extra_features",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": [
                                {
                                    "asset": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                                    "attribute": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                                },
                                {
                                    "asset": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                                    "attribute": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                                },
                            ],
                            "value_type": "Number",
                        },
                    ],
                    "name": "forecast_routine",
                    "output": [
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "predictions",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": {
                                "asset": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                                "attribute": "f1aefe25-ac8d-490e-8ad1-21d3a3de0c08",
                            },
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "MAE",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "MAPE",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                        {
                            "choices": None,
                            "depends_on": None,
                            "description": "",
                            "multiple": False,
                            "name": "R2",
                            "required": False,
                            "sensitive": False,
                            "type": "DataAddress",
                            "value": None,
                            "value_type": "Number",
                        },
                    ],
                    "status": "running",
                    "type": "ForecastRoutine",
                }
            ],
            "version": "LightSplightForecaster-1.0.3",
        }
    ],
    "imported_assets": [],
    "imported_components": [],
}

TEST_STATE_MISSING_ADDRESS = StateSolution.parse_obj(TEST_PLAN.copy())
TEST_STATE_MISSING_ADDRESS.components[0].routines[0].output[0].value = {
    "asset": "local.{{test_asset}}",
    "attribute": "attr_5",
}
TEST_STATE_MISSING_ADDRESS = to_dict(TEST_STATE_MISSING_ADDRESS)

TEST_STATE_MISSING_ADDRESS_2 = StateSolution.parse_obj(TEST_PLAN.copy())
TEST_STATE_MISSING_ADDRESS_2.components[0].routines[0].input[2].value[0] = {
    "asset": "local.{{test_asset2}}",
    "attribute": "attr_4",
}
TEST_STATE_MISSING_ADDRESS_2 = to_dict(TEST_STATE_MISSING_ADDRESS_2)


def get_plan():
    return deepcopy(TEST_PLAN)


def get_state():
    return deepcopy(TEST_STATE_FILLED)
