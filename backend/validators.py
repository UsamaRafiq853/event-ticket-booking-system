from datetime import datetime


def validate_event(data):
    errors = []

    title = str(data.get("title", "")).strip()
    venue = str(data.get("venue", "")).strip()
    event_date = str(data.get("date", "")).strip()
    category = str(data.get("category", "")).strip()

    try:
        price = float(data.get("price", 0))
    except (TypeError, ValueError):
        price = -1

    try:
        total_tickets = int(data.get("totalTickets", 0))
    except (TypeError, ValueError):
        total_tickets = -1

    if len(title) < 3:
        errors.append("Title must contain at least 3 characters")

    if not venue:
        errors.append("Venue is required")

    if not category:
        errors.append("Category is required")

    try:
        datetime.fromisoformat(event_date)
    except (TypeError, ValueError):
        errors.append("A valid event date is required")

    if price < 0:
        errors.append("Price cannot be negative")

    if total_tickets < 1:
        errors.append("Total tickets must be at least 1")

    return errors