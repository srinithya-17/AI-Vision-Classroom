"""In-memory shared state for local AI Virtual Classroom sessions.

This module deliberately has no FastAPI dependency.  It can be connected to
routes or WebSockets in a later phase while remaining useful for local demos.
State is process-local and is lost when the Python process stops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class ClassroomState:
    """Mutable state shared by one classroom session."""

    session_id: str
    teacher: str
    students: set[str] = field(default_factory=set)
    current_slide: int = 1
    total_slides: int = 1
    active_poll: dict[str, Any] | None = None
    raised_hands: set[str] = field(default_factory=set)
    whiteboard: list[Any] = field(default_factory=list)
    pointer_position: dict[str, float] | None = None
    physics_lab_active: bool = False
    physics: dict[str, dict[str, Any]] = field(default_factory=dict)
    recent_gestures: dict[str, dict[str, Any]] = field(default_factory=dict)
    notifications: list[dict[str, Any]] = field(default_factory=list)


class ClassroomStateManager:
    """Manage process-local :class:`ClassroomState` objects by session ID."""

    def __init__(self) -> None:
        self._classrooms: dict[str, ClassroomState] = {}

    def create_classroom(
        self,
        teacher: str,
        session_id: str | None = None,
        total_slides: int = 1,
    ) -> ClassroomState:
        """Create and return a classroom, or return an existing session."""
        if total_slides < 1:
            raise ValueError("total_slides must be at least 1")

        classroom_id = session_id or uuid4().hex
        if classroom_id not in self._classrooms:
            self._classrooms[classroom_id] = ClassroomState(
                session_id=classroom_id,
                teacher=teacher,
                total_slides=total_slides,
            )

        return self._classrooms[classroom_id]

    def get_classroom(self, session_id: str) -> ClassroomState | None:
        """Return a classroom state when the session exists."""
        return self._classrooms.get(session_id)

    def add_student(self, session_id: str, student: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.students.add(student)
        return classroom

    def remove_student(self, session_id: str, student: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.students.discard(student)
        classroom.raised_hands.discard(student)
        return classroom

    def update_current_slide(
        self, session_id: str, current_slide: int
    ) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        if not 1 <= current_slide <= classroom.total_slides:
            raise ValueError("current_slide must be between 1 and total_slides")
        classroom.current_slide = current_slide
        return classroom

    def raise_hand(self, session_id: str, student: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.students.add(student)
        classroom.raised_hands.add(student)
        return classroom

    def dismiss_raised_hand(self, session_id: str, student: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.raised_hands.discard(student)
        return classroom

    def start_poll(
        self, session_id: str, poll: dict[str, Any]
    ) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.active_poll = dict(poll)
        return classroom

    def end_poll(self, session_id: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.active_poll = None
        return classroom

    def update_pointer_position(
        self, session_id: str, x: float, y: float
    ) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.pointer_position = {"x": float(x), "y": float(y)}
        return classroom

    def add_whiteboard_data(
        self, session_id: str, data: Any
    ) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.whiteboard.append(data)
        return classroom

    def clear_whiteboard(self, session_id: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.whiteboard.clear()
        return classroom

    def start_physics_lab(self, session_id: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.physics_lab_active = True
        return classroom

    def end_physics_lab(self, session_id: str) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.physics_lab_active = False
        return classroom

    def update_physics(
        self,
        session_id: str,
        student: str,
        physics_update: dict[str, Any],
    ) -> ClassroomState:
        """Store the latest combined physics update for one student."""
        classroom = self._require_classroom(session_id)
        classroom.students.add(student)
        classroom.physics[student] = dict(physics_update)
        return classroom

    def update_gesture(
        self,
        session_id: str,
        student: str,
        gesture: str,
        timestamp: str,
    ) -> ClassroomState:
        """Store the most recent stable gesture for dashboard display."""
        classroom = self._require_classroom(session_id)
        classroom.students.add(student)
        classroom.recent_gestures[student] = {
            "gesture": gesture,
            "timestamp": timestamp,
        }
        return classroom

    def add_notification(
        self, session_id: str, message: str, level: str = "info"
    ) -> ClassroomState:
        classroom = self._require_classroom(session_id)
        classroom.notifications.append(
            {
                "message": message,
                "level": level,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return classroom

    def _require_classroom(self, session_id: str) -> ClassroomState:
        classroom = self.get_classroom(session_id)
        if classroom is None:
            raise KeyError(f"Classroom session not found: {session_id}")
        return classroom


# A module-level manager is sufficient for the current local/demo process.
classroom_state_manager = ClassroomStateManager()
