import json
import os
from datetime import datetime

import requests


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_FILE = os.path.join(BASE_DIR, "events", "latest_event.json")

# FastAPI backend
BACKEND_URL = os.getenv(
    "CLASSROOM_API_URL",
    "http://127.0.0.1:8000/events"
)

CLASSROOM_STATE_URL = os.getenv(
    "CLASSROOM_STATE_URL",
    "http://127.0.0.1:8000"
)


def save_event(student, event_type, value, confidence=None):

    event = {
        "student": student,
        "event_type": event_type,
        "value": value,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    if confidence is not None:
        event["confidence"] = round(float(confidence), 2)

    # Save local event as before
    with open(
        EVENT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            event,
            file,
            indent=4
        )

    # Send event to FastAPI backend
    try:

        response = requests.post(
            BACKEND_URL,
            json=event,
            timeout=3
        )

        response.raise_for_status()

        print(
            f"Event sent to backend: {event_type}"
        )

    except requests.RequestException as error:

        print(
            f"Backend event send failed: {error}"
        )

    # Hand events are emitted by app.py only when the stable hand state
    # changes. Mirror those transitions to shared classroom state without
    # changing the existing latest_event.json or /events behavior.
    if event_type == "HAND_RAISED":
        _update_classroom_hand_state(student, "raise")

    elif event_type == "HAND_DOWN":
        _update_classroom_hand_state(student, "clear")


def _update_classroom_hand_state(student, action):
    """Best-effort sync of one hand-state transition to FastAPI."""
    try:
        response = requests.post(
            f"{CLASSROOM_STATE_URL}/classroom/hand/{student}/{action}",
            timeout=3
        )
        response.raise_for_status()

        print(
            f"Classroom hand state updated: {student} {action}"
        )

    except requests.RequestException as error:
        # A temporary backend outage must not interrupt camera processing.
        print(
            f"Classroom hand state update failed: {error}"
        )


def get_latest_event():

    if not os.path.exists(EVENT_FILE):
        return None

    try:

        with open(
            EVENT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return None
