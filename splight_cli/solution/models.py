from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from splight_lib.models import Asset, File, Function, RoutineObject
from splight_lib.models.component import Component as LibComponent


class ElementType(str, Enum):
    asset = "asset"
    component = "component"
    function = "function"


class Component(LibComponent):
    routines: List[RoutineObject] = []


class PlanSolution(BaseModel):
    assets: List[Asset]
    components: List[Component]
    files: List[File]
    functions: List[Function]
    imported_assets: Optional[List[Asset]] = Field(default_factory=list)
    imported_components: Optional[List[Component]] = Field(
        default_factory=list
    )
    imported_functions: Optional[List[Function]] = Field(default_factory=list)


class StateSolution(PlanSolution):
    ...
