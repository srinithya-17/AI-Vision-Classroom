from pydantic import BaseModel
from typing import Any


class ClassroomEvent(BaseModel):
    student: str
    event_type: str
    value: Any
    timestamp: str