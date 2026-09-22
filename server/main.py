from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.classroom_state import classroom_state_manager
from server.events import ClassroomEvent
from server.event_store import add_event, get_events


app = FastAPI(title="AI Vision Classroom API")

DEFAULT_CLASSROOM_SESSION_ID = "default-classroom"
classroom_state_manager.create_classroom(
    teacher="Demo Teacher",
    session_id=DEFAULT_CLASSROOM_SESSION_ID,
)


class StudentRequest(BaseModel):
    name: str


class SlideRequest(BaseModel):
    slide_number: int


class PhysicsUpdateRequest(BaseModel):
    elbow_angle: float
    knee_angle: float
    velocity: float
    acceleration: float
    timestamp: str

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

    if event.event_type == "HAND_RAISED":
        classroom_state_manager.raise_hand(
            DEFAULT_CLASSROOM_SESSION_ID,
            event.student,
        )

    elif event.event_type == "HAND_DOWN":
        classroom_state_manager.dismiss_raised_hand(
            DEFAULT_CLASSROOM_SESSION_ID,
            event.student,
        )

    elif event.event_type == "GESTURE_DETECTED":
        classroom_state_manager.update_gesture(
            DEFAULT_CLASSROOM_SESSION_ID,
            event.student,
            str(event.value),
            event.timestamp,
        )

    return {
        "message": "Event received successfully",
        "event": event
    }


@app.get("/events")
def read_events():
    return {
        "events": get_events()
    }


@app.get("/classroom/state")
def get_classroom_state():
    return classroom_state_manager.get_classroom(
        DEFAULT_CLASSROOM_SESSION_ID
    )


@app.post("/classroom/students")
def add_classroom_student(student: StudentRequest):
    return classroom_state_manager.add_student(
        DEFAULT_CLASSROOM_SESSION_ID,
        student.name,
    )


@app.delete("/classroom/students/{student_name}")
def remove_classroom_student(student_name: str):
    return classroom_state_manager.remove_student(
        DEFAULT_CLASSROOM_SESSION_ID,
        student_name,
    )


@app.post("/classroom/slide")
def update_classroom_slide(slide: SlideRequest):
    return classroom_state_manager.update_current_slide(
        DEFAULT_CLASSROOM_SESSION_ID,
        slide.slide_number,
    )


@app.post("/classroom/hand/{student_name}/raise")
def raise_classroom_hand(student_name: str):
    return classroom_state_manager.raise_hand(
        DEFAULT_CLASSROOM_SESSION_ID,
        student_name,
    )


@app.post("/classroom/hand/{student_name}/clear")
def clear_classroom_hand(student_name: str):
    return classroom_state_manager.dismiss_raised_hand(
        DEFAULT_CLASSROOM_SESSION_ID,
        student_name,
    )


@app.post("/classroom/physics/start")
def start_classroom_physics_lab():
    return classroom_state_manager.start_physics_lab(
        DEFAULT_CLASSROOM_SESSION_ID
    )


@app.post("/classroom/physics/end")
def end_classroom_physics_lab():
    return classroom_state_manager.end_physics_lab(
        DEFAULT_CLASSROOM_SESSION_ID
    )


@app.post("/classroom/physics/{student_name}")
def update_student_physics(
    student_name: str,
    physics_update: PhysicsUpdateRequest,
):
    return classroom_state_manager.update_physics(
        DEFAULT_CLASSROOM_SESSION_ID,
        student_name,
        physics_update.model_dump(),
    )
