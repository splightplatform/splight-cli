from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from splight_lib.models import (
    Alert,
    Asset,
    File,
    Function,
    RoutineObject,
    Secret,
)
from splight_lib.models.component import Component as LibComponent


class ElementType(str, Enum):
    asset = "asset"
    secret = "secret"
    component = "component"
    function = "function"
    alert = "alert"


class Component(LibComponent):
    routines: List[RoutineObject] = []


class PlanSolution(BaseModel):
    assets: List[Asset]
    secrets: List[Secret]
    files: List[File]
    components: List[Component]
    functions: List[Function]
    alerts: List[Alert]
    imported_assets: Optional[List[Asset]] = Field(default_factory=list)
    imported_secrets: Optional[List[Secret]] = Field(default_factory=list)
    imported_components: Optional[List[Component]] = Field(
        default_factory=list
    )
    imported_functions: Optional[List[Function]] = Field(default_factory=list)
    imported_alerts: Optional[List[Alert]] = Field(default_factory=list)


class StateSolution(PlanSolution):
    ...
