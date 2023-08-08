from enum import Enum


class ChoiceMixin(str, Enum):
    @classmethod
    def choices(cls):
        return [(key.value.lower(), key.name.capitalize()) for key in cls]


class BuildStatus(ChoiceMixin):
    PENDING = "pending"
    BUILDING = "building"
    FAILED = "failed"
    SUCCESS = "success"
    UNKNOWN = "unknown"
