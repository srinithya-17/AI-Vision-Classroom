const API_URL = "http://127.0.0.1:8000/events";
const CLASSROOM_STATE_URL = "http://127.0.0.1:8000/classroom/state";


async function loadEvents() {

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Failed to fetch events");
        }

        const data = await response.json();

        const events = data.events || [];

        updateSummary(events);
        displayEvents(events);

    } catch (error) {

        console.error("Error:", error);

    }
}


async function loadClassroomState() {

    try {

        const response = await fetch(CLASSROOM_STATE_URL);

        if (!response.ok) {
            throw new Error("Failed to fetch classroom state");
        }

        const state = await response.json();

        updateClassroomSummary(state);
        displayStudentState(state);

    } catch (error) {

        console.error("Classroom state error:", error);

    }
}


function updateSummary(events) {
    document.getElementById("totalEvents").textContent =
        events.length;
}


function displayEvents(events) {

    const table = document.getElementById("eventTable");

    table.innerHTML = "";

    if (events.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="4">
                    No events received yet.
                </td>
            </tr>
        `;

        return;
    }


    events.forEach(event => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${event.student}</td>
            <td>${event.event_type}</td>
            <td>${event.value}</td>
            <td>${event.timestamp}</td>
        `;

        table.appendChild(row);

    });
}


function updateClassroomSummary(state) {

    const students = state.students || [];
    const raisedHands = state.raised_hands || [];

    document.getElementById("activeStudents").textContent =
        students.length;

    document.getElementById("raisedHands").textContent =
        raisedHands.length;

    document.getElementById("physicsLabStatus").textContent =
        state.physics_lab_active ? "Active" : "Inactive";
}


function displayStudentState(state) {

    const table = document.getElementById("studentStateTable");
    const students = state.students || [];
    const raisedHands = state.raised_hands || [];
    const physics = state.physics || {};
    const gestures = state.recent_gestures || {};

    table.innerHTML = "";

    if (students.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="7">No students have joined yet.</td>
            </tr>
        `;
        return;
    }

    students.forEach(student => {

        const row = document.createElement("tr");
        const studentPhysics = physics[student] || {};
        const studentGesture = gestures[student] || {};
        const cells = [
            student,
            raisedHands.includes(student) ? "Raised" : "Down",
            studentGesture.gesture || "—",
            formatNumber(studentPhysics.elbow_angle, 1),
            formatNumber(studentPhysics.knee_angle, 1),
            formatNumber(studentPhysics.velocity, 3),
            formatNumber(studentPhysics.acceleration, 3),
        ];

        cells.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        table.appendChild(row);
    });
}


function formatNumber(value, digits) {

    return typeof value === "number" ? value.toFixed(digits) : "—";
}


// Load events when page opens
loadEvents();
loadClassroomState();


// Refresh events every 3 seconds
setInterval(loadEvents, 3000);
setInterval(loadClassroomState, 3000);
