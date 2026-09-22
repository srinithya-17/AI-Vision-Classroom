"""Non-camera integration checks for the Phase 5 classroom flow."""

import ast
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VISION_ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(PROJECT_ROOT), str(VISION_ROOT)]

from fastapi.encoders import jsonable_encoder

from physics_engine import PhysicsEngine
from server.event_store import events
from server.events import ClassroomEvent
from server.main import (
    PhysicsUpdateRequest,
    StudentRequest,
    add_classroom_student,
    get_classroom_state,
    read_events,
    receive_event,
    update_student_physics,
)
from server.classroom_state import classroom_state_manager


def landmark(x=0.0, y=0.0):
    return SimpleNamespace(x=x, y=y)


def pose(wrist_x):
    """Create the subset of MediaPipe pose landmarks used by PhysicsEngine."""
    points = [landmark() for _ in range(33)]
    points[11], points[13], points[15] = landmark(0, 0), landmark(0, 1), landmark(wrist_x, 1)
    points[12], points[14], points[16] = landmark(2, 0), landmark(2, 1), landmark(2 + wrist_x, 1)
    points[23], points[25], points[27] = landmark(0, 2), landmark(0, 3), landmark(1, 3)
    points[24], points[26], points[28] = landmark(2, 2), landmark(2, 3), landmark(3, 3)
    return points


def app_normalize_google_meet_url(value):
    """Execute the production helper without loading Streamlit or a webcam."""
    source = (VISION_ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "normalize_google_meet_url"
    )
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"re": __import__("re"), "urlparse": urlparse}
    exec(compile(ast.fix_missing_locations(module), "app.py", "exec"), namespace)
    return namespace["normalize_google_meet_url"](value)


class Phase5IntegrationTests(unittest.TestCase):
    def setUp(self):
        events.clear()
        state = classroom_state_manager.get_classroom("default-classroom")
        state.students.clear()
        state.raised_hands.clear()
        state.physics.clear()
        state.recent_gestures.clear()

    def test_student_events_physics_and_dashboard_state(self):
        student = "Phase5 Student"
        add_classroom_student(StudentRequest(name=student))

        raised = receive_event(ClassroomEvent(**{
            "student": student, "event_type": "HAND_RAISED", "value": True,
            "timestamp": "2026-09-22T10:00:00",
        }))
        self.assertEqual(raised["message"], "Event received successfully")
        self.assertIn(student, get_classroom_state().raised_hands)

        gesture = receive_event(ClassroomEvent(**{
            "student": student, "event_type": "GESTURE_DETECTED", "value": "THUMBS_UP",
            "timestamp": "2026-09-22T10:00:01",
        }))
        self.assertEqual(gesture["message"], "Event received successfully")

        engine = PhysicsEngine()
        first = engine.process_landmarks(pose(0.0), 1.0)
        second = engine.process_landmarks(pose(0.1), 2.0)
        physics = engine.process_landmarks(pose(0.3), 3.0)
        self.assertNotEqual(first["elbow_angle"], second["elbow_angle"])
        self.assertGreater(second["velocity"], 0)
        self.assertNotEqual(physics["acceleration"], 0)
        self.assertEqual(set(physics), {"elbow_angle", "knee_angle", "velocity", "acceleration"})

        snapshot = {**physics, "timestamp": "2026-09-22T10:00:02"}
        update_student_physics(student, PhysicsUpdateRequest(**snapshot))

        body = jsonable_encoder(get_classroom_state())
        self.assertIn(student, body["students"])
        self.assertEqual(body["recent_gestures"][student]["gesture"], "THUMBS_UP")
        self.assertEqual(body["physics"][student], snapshot)
        self.assertEqual(len(read_events()["events"]), 2)

        lowered = receive_event(ClassroomEvent(**{
            "student": student, "event_type": "HAND_DOWN", "value": False,
            "timestamp": "2026-09-22T10:00:03",
        }))
        self.assertEqual(lowered["message"], "Event received successfully")
        self.assertNotIn(student, get_classroom_state().raised_hands)

    def test_google_meet_normalization(self):
        valid = "https://meet.google.com/abc-defg-hij"
        self.assertEqual(app_normalize_google_meet_url(valid), valid)
        self.assertEqual(app_normalize_google_meet_url(valid.removeprefix("https://")), valid)
        self.assertIsNone(app_normalize_google_meet_url("https://example.com/abc-defg-hij"))
        self.assertIsNone(app_normalize_google_meet_url("https://meet.google.com/not-a-meeting"))


if __name__ == "__main__":
    unittest.main()
