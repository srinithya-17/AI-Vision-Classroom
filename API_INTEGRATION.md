
# AI Vision Classroom API

## Backend URL

For local testing:

http://127.0.0.1:8000

## Send Classroom Event

### POST /events

Send an event to the backend.

Example:

```json
{
  "student": "Student1",
  "event_type": "HAND_RAISED",
  "value": true,
  "timestamp": "2026-09-08T14:55:00"
}