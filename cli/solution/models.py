from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from splight_lib.models import Asset, RoutineObject
from splight_lib.models.component import Component as LibComponent


class ElementType(str, Enum):
    asset = "asset"
    component = "component"


class Component(LibComponent):
    routines: List[RoutineObject] = []


class Solution(BaseModel):
    assets: List[Asset]
    components: List[Component]
    imported_assets: Optional[List[Asset]] = []
    imported_components: Optional[List[Component]] = []
