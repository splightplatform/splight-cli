from typing import List, Optional

from pydantic import BaseModel
from splight_lib.models.base import SplightDatabaseBaseModel
from splight_lib.models.component import (
    Asset,
    Binding,
    Command,
    ComponentType,
    CustomType,
    Endpoint,
    InputDataAddress,
    InputParameter,
    Output,
    RoutineStatus,
)


class SplightObject(SplightDatabaseBaseModel):
    id: Optional[str]
    name: str
    component_id: Optional[str]
    description: Optional[str] = ""
    type: str


class RoutineObject(SplightObject):
    status: Optional[RoutineStatus] = RoutineStatus.RUNNING

    config: Optional[List[InputParameter]] = []
    input: List[InputDataAddress] = []
    output: List[InputDataAddress] = []


class Component(SplightDatabaseBaseModel):
    id: Optional[str]
    name: Optional[str]
    version: str
    custom_types: List[CustomType] = []
    component_type: ComponentType = ComponentType.CONNECTOR
    input: List[InputParameter] = []
    output: List[Output] = []
    commands: List[Command] = []
    endpoints: List[Endpoint] = []
    bindings: List[Binding] = []
    routines: List[RoutineObject] = []


class Solution(BaseModel):
    assets: List[Asset]
    components: List[Component]
