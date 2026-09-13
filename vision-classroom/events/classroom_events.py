from datetime import datetime


def create_event(
    student_name,
    event_type,
    value,
    confidence=None
):
    event = {
        "student": student_name,
        "event_type": event_type,
        "value": value,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    if confidence is not None:
        event["confidence"] = round(float(confidence), 2)

    return event