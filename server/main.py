from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.events import ClassroomEvent
from server.event_store import add_event, get_events


app = FastAPI(title="AI Vision Classroom API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "AI Vision Classroom Backend is running"
    }


@app.post("/events")
def receive_event(event: ClassroomEvent):
    add_event(event)

    return {
        "message": "Event received successfully",
        "event": event
    }


@app.get("/events")
def read_events():
    return {
        "events": get_events()
    }