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


def validate_booking(data):
    errors = []

    customer_name = str(data.get("customerName", "")).strip()
    customer_email = str(data.get("customerEmail", "")).strip()
    event_id = str(data.get("eventId", "")).strip()

    try:
        ticket_quantity = int(data.get("ticketQuantity", 0))
    except (TypeError, ValueError):
        ticket_quantity = -1

    if len(customer_name) < 3:
        errors.append("Customer name must contain at least 3 characters")

    if not customer_email or "@" not in customer_email:
        errors.append("A valid customer email is required")

    if not event_id:
        errors.append("Event ID is required")

    if ticket_quantity < 1:
        errors.append("Ticket quantity must be at least 1")

    return errors