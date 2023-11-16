from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from splight_lib.models import Asset, RoutineObject
from splight_lib.models.component import Component as LibComponent


class ElementType(str, Enum):
    asset = "asset"
    component = "component"


class Component(LibComponent):
    routines: List[RoutineObject] = []


class PlanSolution(BaseModel):
    assets: List[Asset]
    components: List[Component]
    imported_assets: Optional[List[Asset]] = Field(default_factory=list)
    imported_components: Optional[List[Component]] = Field(
        default_factory=list
    )


class StateSolution(PlanSolution):
    ...
