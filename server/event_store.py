from typing import List
from server.events import ClassroomEvent


events: List[ClassroomEvent] = []


def add_event(event: ClassroomEvent):
    events.append(event)


def get_events():
    return events