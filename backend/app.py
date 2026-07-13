from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo.errors import PyMongoError

from config import Config
from database import check_database_connection, get_database
from validators import validate_event


app = Flask(__name__)
CORS(app)


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


if __name__ == "__main__":
    app.run(
        debug=Config.FLASK_DEBUG,
        port=Config.PORT,
        use_reloader=False,
    )