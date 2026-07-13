from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo.errors import PyMongoError

from config import Config
from database import check_database_connection, get_database
from validators import validate_event


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


def parse_event_id(event_id):
    try:
        return ObjectId(event_id)
    except InvalidId:
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
    object_id = parse_event_id(event_id)

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
    object_id = parse_event_id(event_id)

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


if __name__ == "__main__":
    app.run(
        debug=Config.FLASK_DEBUG,
        port=Config.PORT,
        use_reloader=False,
    )