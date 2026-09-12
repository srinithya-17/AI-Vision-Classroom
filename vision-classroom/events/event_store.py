import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENT_FILE = os.path.join(BASE_DIR, "events", "latest_event.json")


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