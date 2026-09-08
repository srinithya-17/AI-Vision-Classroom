const API_URL = "http://127.0.0.1:8000/events";


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


function updateSummary(events) {

    const students = new Set(
        events.map(event => event.student)
    );

    const raisedHands = events.filter(
        event =>
            event.event_type === "HAND_RAISED" &&
            event.value === true
    );

    document.getElementById("activeStudents").textContent =
        students.size;

    document.getElementById("raisedHands").textContent =
        raisedHands.length;

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


// Load events when page opens
loadEvents();


// Refresh events every 3 seconds
setInterval(loadEvents, 3000);