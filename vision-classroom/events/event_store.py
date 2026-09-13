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