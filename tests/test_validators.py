import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))

from validators import validate_booking, validate_event


def test_valid_event_data():
    event = {
        "title": "Technology Conference",
        "venue": "Dublin Convention Centre",
        "date": "2026-09-20T10:00:00",
        "category": "Technology",
        "price": 25,
        "totalTickets": 100,
    }

    assert validate_event(event) == []


def test_invalid_event_data():
    event = {
        "title": "A",
        "venue": "",
        "date": "invalid-date",
        "category": "",
        "price": -10,
        "totalTickets": 0,
    }

    errors = validate_event(event)

    assert "Title must contain at least 3 characters" in errors
    assert "Venue is required" in errors
    assert "Category is required" in errors
    assert "A valid event date is required" in errors
    assert "Price cannot be negative" in errors
    assert "Total tickets must be at least 1" in errors


def test_valid_booking_data():
    booking = {
        "eventId": "6a556fb5792e41ca87030852",
        "customerName": "John Smith",
        "customerEmail": "john@example.com",
        "ticketQuantity": 2,
    }

    assert validate_booking(booking) == []


def test_invalid_booking_data():
    booking = {
        "eventId": "",
        "customerName": "A",
        "customerEmail": "invalid-email",
        "ticketQuantity": 0,
    }

    errors = validate_booking(booking)

    assert "Customer name must contain at least 3 characters" in errors
    assert "A valid customer email is required" in errors
    assert "Event ID is required" in errors
    assert "Ticket quantity must be at least 1" in errors