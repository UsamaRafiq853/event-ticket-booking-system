from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from config import Config
from database import check_database_connection, get_database
from validators import validate_booking, validate_event


app = Flask(__name__)
CORS(app)


def serialize_event(event):
    return {
        "_id": str(event["_id"]),
        "title": event.get("title", ""),
        "venue": event.get("venue", ""),
        "date": event.get("date", ""),
        "category": event.get("category", ""),
        "price": event.get("price", 0),
        "totalTickets": event.get("totalTickets", 0),
        "availableTickets": event.get("availableTickets", 0),
        "status": event.get("status", "Active"),
        "createdAt": (
            event["createdAt"].isoformat()
            if isinstance(event.get("createdAt"), datetime)
            else event.get("createdAt")
        ),
        "updatedAt": (
            event["updatedAt"].isoformat()
            if isinstance(event.get("updatedAt"), datetime)
            else event.get("updatedAt")
        ),
    }


def serialize_booking(booking):
    return {
        "_id": str(booking["_id"]),
        "eventId": str(booking.get("eventId", "")),
        "eventTitle": booking.get("eventTitle", ""),
        "customerName": booking.get("customerName", ""),
        "customerEmail": booking.get("customerEmail", ""),
        "ticketQuantity": booking.get("ticketQuantity", 0),
        "pricePerTicket": booking.get("pricePerTicket", 0),
        "totalAmount": booking.get("totalAmount", 0),
        "status": booking.get("status", "Confirmed"),
        "bookedAt": (
            booking["bookedAt"].isoformat()
            if isinstance(booking.get("bookedAt"), datetime)
            else booking.get("bookedAt")
        ),
    }


def parse_object_id(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "project": "Event Ticket Booking System",
            "status": "Backend Running",
        }
    ), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "success": True,
            "message": "API is running successfully",
        }
    ), 200


@app.route("/api/database-health", methods=["GET"])
def database_health():
    success, message = check_database_connection()
    status_code = 200 if success else 500

    return jsonify(
        {
            "success": success,
            "message": message,
        }
    ), status_code


@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        database = get_database()
        events = list(database.events.find().sort("createdAt", -1))

        return jsonify(
            {
                "success": True,
                "count": len(events),
                "events": [serialize_event(event) for event in events],
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to retrieve events",
                "error": str(error),
            }
        ), 500


@app.route("/api/events/<event_id>", methods=["GET"])
def get_event(event_id):
    object_id = parse_object_id(event_id)

    if object_id is None:
        return jsonify(
            {
                "success": False,
                "message": "Invalid event ID",
            }
        ), 400

    try:
        database = get_database()
        event = database.events.find_one({"_id": object_id})

        if event is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Event not found",
                }
            ), 404

        return jsonify(
            {
                "success": True,
                "event": serialize_event(event),
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to retrieve event",
                "error": str(error),
            }
        ), 500


@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "success": False,
                "message": "A valid JSON request body is required",
            }
        ), 400

    errors = validate_event(data)

    if errors:
        return jsonify(
            {
                "success": False,
                "message": "Event validation failed",
                "errors": errors,
            }
        ), 400

    try:
        database = get_database()

        event = {
            "title": str(data["title"]).strip(),
            "venue": str(data["venue"]).strip(),
            "date": str(data["date"]).strip(),
            "category": str(data["category"]).strip(),
            "price": float(data["price"]),
            "totalTickets": int(data["totalTickets"]),
            "availableTickets": int(data["totalTickets"]),
            "status": "Active",
            "createdAt": datetime.now(timezone.utc),
        }

        result = database.events.insert_one(event)

        return jsonify(
            {
                "success": True,
                "message": "Event created successfully",
                "eventId": str(result.inserted_id),
            }
        ), 201

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to create event",
                "error": str(error),
            }
        ), 500


@app.route("/api/events/<event_id>", methods=["PUT"])
def update_event(event_id):
    object_id = parse_object_id(event_id)

    if object_id is None:
        return jsonify(
            {
                "success": False,
                "message": "Invalid event ID",
            }
        ), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "success": False,
                "message": "A valid JSON request body is required",
            }
        ), 400

    errors = validate_event(data)

    if errors:
        return jsonify(
            {
                "success": False,
                "message": "Event validation failed",
                "errors": errors,
            }
        ), 400

    try:
        database = get_database()
        existing_event = database.events.find_one({"_id": object_id})

        if existing_event is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Event not found",
                }
            ), 404

        total_tickets = int(data["totalTickets"])
        tickets_sold = (
            existing_event.get("totalTickets", 0)
            - existing_event.get("availableTickets", 0)
        )

        if total_tickets < tickets_sold:
            return jsonify(
                {
                    "success": False,
                    "message": (
                        "Total tickets cannot be lower than tickets already sold"
                    ),
                }
            ), 400

        updated_event = {
            "title": str(data["title"]).strip(),
            "venue": str(data["venue"]).strip(),
            "date": str(data["date"]).strip(),
            "category": str(data["category"]).strip(),
            "price": float(data["price"]),
            "totalTickets": total_tickets,
            "availableTickets": total_tickets - tickets_sold,
            "status": str(
                data.get("status", existing_event.get("status", "Active"))
            ).strip(),
            "updatedAt": datetime.now(timezone.utc),
        }

        database.events.update_one(
            {"_id": object_id},
            {"$set": updated_event},
        )

        event = database.events.find_one({"_id": object_id})

        return jsonify(
            {
                "success": True,
                "message": "Event updated successfully",
                "event": serialize_event(event),
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to update event",
                "error": str(error),
            }
        ), 500


@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    object_id = parse_object_id(event_id)

    if object_id is None:
        return jsonify(
            {
                "success": False,
                "message": "Invalid event ID",
            }
        ), 400

    try:
        database = get_database()
        result = database.events.delete_one({"_id": object_id})

        if result.deleted_count == 0:
            return jsonify(
                {
                    "success": False,
                    "message": "Event not found",
                }
            ), 404

        return jsonify(
            {
                "success": True,
                "message": "Event deleted successfully",
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to delete event",
                "error": str(error),
            }
        ), 500


@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    try:
        database = get_database()
        bookings = list(database.bookings.find().sort("bookedAt", -1))

        return jsonify(
            {
                "success": True,
                "count": len(bookings),
                "bookings": [
                    serialize_booking(booking)
                    for booking in bookings
                ],
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to retrieve bookings",
                "error": str(error),
            }
        ), 500


@app.route("/api/bookings/<booking_id>", methods=["GET"])
def get_booking(booking_id):
    object_id = parse_object_id(booking_id)

    if object_id is None:
        return jsonify(
            {
                "success": False,
                "message": "Invalid booking ID",
            }
        ), 400

    try:
        database = get_database()
        booking = database.bookings.find_one({"_id": object_id})

        if booking is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Booking not found",
                }
            ), 404

        return jsonify(
            {
                "success": True,
                "booking": serialize_booking(booking),
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to retrieve booking",
                "error": str(error),
            }
        ), 500


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "success": False,
                "message": "A valid JSON request body is required",
            }
        ), 400

    errors = validate_booking(data)

    if errors:
        return jsonify(
            {
                "success": False,
                "message": "Booking validation failed",
                "errors": errors,
            }
        ), 400

    event_object_id = parse_object_id(data.get("eventId"))

    if event_object_id is None:
        return jsonify(
            {
                "success": False,
                "message": "Invalid event ID",
            }
        ), 400

    ticket_quantity = int(data["ticketQuantity"])

    try:
        database = get_database()
        event = database.events.find_one({"_id": event_object_id})

        if event is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Event not found",
                }
            ), 404

        if event.get("status") != "Active":
            return jsonify(
                {
                    "success": False,
                    "message": "Bookings are not available for this event",
                }
            ), 400

        updated_event = database.events.find_one_and_update(
            {
                "_id": event_object_id,
                "availableTickets": {"$gte": ticket_quantity},
            },
            {
                "$inc": {
                    "availableTickets": -ticket_quantity,
                }
            },
            return_document=ReturnDocument.AFTER,
        )

        if updated_event is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Not enough tickets are available",
                }
            ), 400

        total_amount = float(event.get("price", 0)) * ticket_quantity

        booking = {
            "eventId": event_object_id,
            "eventTitle": event.get("title", ""),
            "customerName": str(data["customerName"]).strip(),
            "customerEmail": str(data["customerEmail"]).strip().lower(),
            "ticketQuantity": ticket_quantity,
            "pricePerTicket": float(event.get("price", 0)),
            "totalAmount": total_amount,
            "status": "Confirmed",
            "bookedAt": datetime.now(timezone.utc),
        }

        try:
            result = database.bookings.insert_one(booking)
        except PyMongoError:
            database.events.update_one(
                {"_id": event_object_id},
                {"$inc": {"availableTickets": ticket_quantity}},
            )
            raise

        created_booking = database.bookings.find_one(
            {"_id": result.inserted_id}
        )

        return jsonify(
            {
                "success": True,
                "message": "Booking created successfully",
                "booking": serialize_booking(created_booking),
            }
        ), 201

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to create booking",
                "error": str(error),
            }
        ), 500

@app.route("/api/bookings/<booking_id>/cancel", methods=["PUT"])
def cancel_booking(booking_id):
    booking_object_id = parse_object_id(booking_id)

    if booking_object_id is None:
        return jsonify(
            {
                "success": False,
                "message": "Invalid booking ID",
            }
        ), 400

    try:
        database = get_database()

        booking = database.bookings.find_one(
            {"_id": booking_object_id}
        )

        if booking is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Booking not found",
                }
            ), 404

        if booking.get("status") == "Cancelled":
            return jsonify(
                {
                    "success": False,
                    "message": "Booking is already cancelled",
                }
            ), 400

        if booking.get("status") != "Confirmed":
            return jsonify(
                {
                    "success": False,
                    "message": "Only confirmed bookings can be cancelled",
                }
            ), 400

        event_object_id = booking.get("eventId")
        ticket_quantity = int(booking.get("ticketQuantity", 0))

        updated_booking = database.bookings.find_one_and_update(
            {
                "_id": booking_object_id,
                "status": "Confirmed",
            },
            {
                "$set": {
                    "status": "Cancelled",
                    "cancelledAt": datetime.now(timezone.utc),
                }
            },
            return_document=ReturnDocument.AFTER,
        )

        if updated_booking is None:
            return jsonify(
                {
                    "success": False,
                    "message": "Booking could not be cancelled",
                }
            ), 409

        try:
            event_result = database.events.update_one(
                {"_id": event_object_id},
                {
                    "$inc": {
                        "availableTickets": ticket_quantity,
                    }
                },
            )

            if event_result.matched_count == 0:
                database.bookings.update_one(
                    {"_id": booking_object_id},
                    {
                        "$set": {
                            "status": "Confirmed",
                        },
                        "$unset": {
                            "cancelledAt": "",
                        },
                    },
                )

                return jsonify(
                    {
                        "success": False,
                        "message": "Related event was not found",
                    }
                ), 404

        except PyMongoError:
            database.bookings.update_one(
                {"_id": booking_object_id},
                {
                    "$set": {
                        "status": "Confirmed",
                    },
                    "$unset": {
                        "cancelledAt": "",
                    },
                },
            )
            raise

        return jsonify(
            {
                "success": True,
                "message": "Booking cancelled successfully",
                "booking": serialize_booking(updated_booking),
            }
        ), 200

    except PyMongoError as error:
        return jsonify(
            {
                "success": False,
                "message": "Unable to cancel booking",
                "error": str(error),
            }
        ), 500

if __name__ == "__main__":
    app.run(
        debug=Config.FLASK_DEBUG,
        port=Config.PORT,
        use_reloader=False,
    )