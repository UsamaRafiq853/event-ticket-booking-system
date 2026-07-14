const API_BASE_URL = "http://127.0.0.1:5000/api";

let allEvents = [];
let allBookings = [];


function setMessage(element, message, type = "") {
    element.textContent = message;
    element.className = `message ${type}`.trim();
}


function formatCurrency(value) {
    return new Intl.NumberFormat("en-IE", {
        style: "currency",
        currency: "EUR"
    }).format(Number(value || 0));
}


function formatDate(value) {
    if (!value) {
        return "Not provided";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("en-IE");
}


async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    const data = await response.json();

    if (!response.ok) {
        const error = new Error(
            data.message || "The request could not be completed"
        );

        error.details = data.errors || [];
        throw error;
    }

    return data;
}


async function checkBackendStatus() {
    const statusElement = document.getElementById("database-status");

    try {
        const response = await apiRequest("/database-health");

        setMessage(
            statusElement,
            response.message,
            "success"
        );
    } catch (error) {
        setMessage(
            statusElement,
            "Backend or database connection is unavailable",
            "error"
        );
    }
}


function createEventCard(event) {
    const card = document.createElement("article");
    card.className = "event-card";

    const hasTickets = Number(event.availableTickets) > 0;
    const canBook = event.status === "Active" && hasTickets;

    card.innerHTML = `
        <span class="badge">${event.status}</span>

        <h3>${event.title}</h3>

        <div class="event-meta">
            <span><strong>Category:</strong> ${event.category}</span>
            <span><strong>Venue:</strong> ${event.venue}</span>
            <span><strong>Date:</strong> ${formatDate(event.date)}</span>
            <span><strong>Price:</strong> ${formatCurrency(event.price)}</span>
            <span>
                <strong>Tickets:</strong>
                ${event.availableTickets} / ${event.totalTickets} available
            </span>
        </div>

        <div class="card-actions">
            <button
                class="button button-primary book-event-button"
                type="button"
                ${canBook ? "" : "disabled"}
            >
                ${canBook ? "Book Tickets" : "Unavailable"}
            </button>
        </div>
    `;

    const bookingButton = card.querySelector(".book-event-button");

    if (canBook) {
        bookingButton.addEventListener("click", () => {
            openBookingModal(event);
        });
    }

    return card;
}


function renderEvents(events) {
    const eventsList = document.getElementById("events-list");
    const message = document.getElementById("events-message");

    eventsList.innerHTML = "";

    if (events.length === 0) {
        setMessage(message, "No events found.");
        return;
    }

    setMessage(message, "");

    events.forEach((event) => {
        eventsList.appendChild(createEventCard(event));
    });
}


async function loadEvents() {
    const message = document.getElementById("events-message");

    setMessage(message, "Loading events...");

    try {
        const response = await apiRequest("/events");
        allEvents = response.events || [];
        filterEvents();
    } catch (error) {
        setMessage(
            message,
            error.message,
            "error"
        );
    }
}


function filterEvents() {
    const searchValue = document
        .getElementById("event-search")
        .value
        .trim()
        .toLowerCase();

    const statusValue = document
        .getElementById("event-status-filter")
        .value;

    const filteredEvents = allEvents.filter((event) => {
        const searchableText = [
            event.title,
            event.venue,
            event.category
        ]
            .join(" ")
            .toLowerCase();

        const matchesSearch = searchableText.includes(searchValue);
        const matchesStatus = !statusValue || event.status === statusValue;

        return matchesSearch && matchesStatus;
    });

    renderEvents(filteredEvents);
}


function renderBookings(bookings) {
    const tableBody = document.getElementById("bookings-table-body");
    const message = document.getElementById("bookings-message");

    tableBody.innerHTML = "";

    if (bookings.length === 0) {
        setMessage(message, "No bookings found.");
        return;
    }

    setMessage(message, "");

    bookings.forEach((booking) => {
        const row = document.createElement("tr");

        const canCancel = booking.status === "Confirmed";

        row.innerHTML = `
            <td>${booking._id.slice(-8)}</td>
            <td>
                <strong>${booking.customerName}</strong><br>
                <small>${booking.customerEmail}</small>
            </td>
            <td>${booking.eventTitle}</td>
            <td>${booking.ticketQuantity}</td>
            <td>${formatCurrency(booking.totalAmount)}</td>
            <td>${booking.status}</td>
            <td>
                <button
                    class="button button-secondary cancel-booking-button"
                    type="button"
                    ${canCancel ? "" : "disabled"}
                >
                    ${canCancel ? "Cancel" : "Cancelled"}
                </button>
            </td>
        `;

        const cancelButton = row.querySelector(".cancel-booking-button");

        if (canCancel) {
            cancelButton.addEventListener("click", () => {
                cancelBooking(booking._id);
            });
        }

        tableBody.appendChild(row);
    });
}


async function loadBookings() {
    const message = document.getElementById("bookings-message");

    setMessage(message, "Loading bookings...");

    try {
        const response = await apiRequest("/bookings");
        allBookings = response.bookings || [];
        filterBookings();
    } catch (error) {
        setMessage(
            message,
            error.message,
            "error"
        );
    }
}


function filterBookings() {
    const searchValue = document
        .getElementById("booking-search")
        .value
        .trim()
        .toLowerCase();

    const filteredBookings = allBookings.filter((booking) => {
        const searchableText = [
            booking.customerName,
            booking.customerEmail,
            booking.eventTitle,
            booking.status
        ]
            .join(" ")
            .toLowerCase();

        return searchableText.includes(searchValue);
    });

    renderBookings(filteredBookings);
}


function openBookingModal(event) {
    const modal = document.getElementById("booking-modal");

    document.getElementById("booking-event-id").value = event._id;
    document.getElementById("booking-event-title").textContent = event.title;
    document.getElementById("ticket-quantity").max =
        event.availableTickets;

    setMessage(
        document.getElementById("booking-form-message"),
        ""
    );

    modal.classList.remove("hidden");
}


function closeBookingModal() {
    document
        .getElementById("booking-modal")
        .classList
        .add("hidden");

    document.getElementById("booking-form").reset();
}


async function createEvent(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const message = document.getElementById("event-form-message");

    const formData = new FormData(form);

    const payload = {
        title: formData.get("title"),
        category: formData.get("category"),
        venue: formData.get("venue"),
        date: formData.get("date"),
        price: Number(formData.get("price")),
        totalTickets: Number(formData.get("totalTickets"))
    };

    setMessage(message, "Creating event...");

    try {
        const response = await apiRequest("/events", {
            method: "POST",
            body: JSON.stringify(payload)
        });

        setMessage(
            message,
            response.message,
            "success"
        );

        form.reset();

        await loadEvents();
    } catch (error) {
        const details = error.details.length
            ? `: ${error.details.join(", ")}`
            : "";

        setMessage(
            message,
            `${error.message}${details}`,
            "error"
        );
    }
}


async function createBooking(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const message = document.getElementById("booking-form-message");
    const formData = new FormData(form);

    const payload = {
        eventId: formData.get("eventId"),
        customerName: formData.get("customerName"),
        customerEmail: formData.get("customerEmail"),
        ticketQuantity: Number(formData.get("ticketQuantity"))
    };

    setMessage(message, "Creating booking...");

    try {
        const response = await apiRequest("/bookings", {
            method: "POST",
            body: JSON.stringify(payload)
        });

        setMessage(
            message,
            response.message,
            "success"
        );

        await Promise.all([
            loadEvents(),
            loadBookings()
        ]);

        setTimeout(() => {
            closeBookingModal();
        }, 800);
    } catch (error) {
        const details = error.details.length
            ? `: ${error.details.join(", ")}`
            : "";

        setMessage(
            message,
            `${error.message}${details}`,
            "error"
        );
    }
}


async function cancelBooking(bookingId) {
    const confirmed = window.confirm(
        "Are you sure you want to cancel this booking?"
    );

    if (!confirmed) {
        return;
    }

    const message = document.getElementById("bookings-message");

    setMessage(message, "Cancelling booking...");

    try {
        const response = await apiRequest(
            `/bookings/${bookingId}/cancel`,
            {
                method: "PUT"
            }
        );

        setMessage(
            message,
            response.message,
            "success"
        );

        await Promise.all([
            loadEvents(),
            loadBookings()
        ]);
    } catch (error) {
        setMessage(
            message,
            error.message,
            "error"
        );
    }
}


function registerEventListeners() {
    document
        .getElementById("refresh-events-button")
        .addEventListener("click", loadEvents);

    document
        .getElementById("refresh-bookings-button")
        .addEventListener("click", loadBookings);

    document
        .getElementById("event-search")
        .addEventListener("input", filterEvents);

    document
        .getElementById("event-status-filter")
        .addEventListener("change", filterEvents);

    document
        .getElementById("booking-search")
        .addEventListener("input", filterBookings);

    document
        .getElementById("event-form")
        .addEventListener("submit", createEvent);

    document
        .getElementById("booking-form")
        .addEventListener("submit", createBooking);

    document
        .getElementById("close-booking-modal")
        .addEventListener("click", closeBookingModal);

    document
        .getElementById("booking-modal")
        .addEventListener("click", (event) => {
            if (event.target.id === "booking-modal") {
                closeBookingModal();
            }
        });
}


async function initialiseApplication() {
    registerEventListeners();

    await checkBackendStatus();

    await Promise.all([
        loadEvents(),
        loadBookings()
    ]);
}


document.addEventListener(
    "DOMContentLoaded",
    initialiseApplication
);